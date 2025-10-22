import json
import time
import uuid
import threading
import asyncio
import base64
from typing import Dict, Any, AsyncGenerator, Tuple, List
from urllib.parse import quote

import cloudscraper
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger

from app.core.config import settings, Credential
from app.utils.sse_utils import create_sse_data, create_chat_completion_chunk, DONE_CHUNK

# 定义一个通用的 User-Agent，模拟真实浏览器
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

class NovaAppProvider:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.cred_manager = CredentialManager(settings.CREDENTIALS)
        # 创建一个可复用的 httpx 客户端实例
        self.http_client = httpx.AsyncClient()

    async def chat_completion(self, request_data: Dict[str, Any]) -> StreamingResponse:
        
        async def stream_generator() -> AsyncGenerator[bytes, None]:
            request_id = f"chatcmpl-{uuid.uuid4()}"
            model_name = request_data.get("model", settings.DEFAULT_MODEL)
            
            try:
                credential = self.cred_manager.get_credential()
                payload, model_id = self._prepare_chat_payload(request_data, model_name)
                headers = self._prepare_chat_headers(credential, model_id)

                logger.info(f"向上游发送聊天请求, 模型: {model_name} (ID: {payload['model']})")
                
                response = self.scraper.post(
                    "https://api.novaapp.ai/api/chat",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=settings.API_REQUEST_TIMEOUT
                )
                
                logger.info(f"上游响应状态码: {response.status_code}")
                response.raise_for_status()

                for line in response.iter_lines():
                    if line.startswith(b"data:"):
                        content = line[len(b"data:"):].strip()
                        if content == b"[DONE]":
                            break
                        try:
                            data = json.loads(content)
                            delta_content = None
                            if "choices" in data:
                                choice = data.get("choices", [{}])[0]
                                if "delta" in choice:
                                    delta_content = choice.get("delta", {}).get("content")
                            
                            if delta_content is not None:
                                chunk = create_chat_completion_chunk(request_id, model_name, delta_content)
                                yield create_sse_data(chunk)
                        except (json.JSONDecodeError, IndexError):
                            if content:
                                logger.warning(f"无法解析 SSE 数据块: {content}")
                            continue
            
                final_chunk = create_chat_completion_chunk(request_id, model_name, "", "stop")
                yield create_sse_data(final_chunk)
                yield DONE_CHUNK

            except Exception as e:
                logger.error(f"处理流时发生错误: {e}", exc_info=True)
                error_message = f"内部服务器错误: {str(e)}"
                error_chunk = create_chat_completion_chunk(request_id, model_name, error_message, "stop")
                yield create_sse_data(error_chunk)
                yield DONE_CHUNK

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    async def generate_image(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = request_data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="参数 'prompt' 不能为空。")

        model_name = request_data.get("model", "nova-dalle3")
        n = request_data.get("n", 1)

        try:
            initial_payload = {"messages": [{"role": "user", "content": prompt}]}
            model_id = settings.MODEL_MAPPING[model_name]
            credential = self.cred_manager.get_credential()
            headers = self._prepare_image_submit_headers(credential, model_id)
            
            logger.info(f"向上游提交图像生成任务, Prompt: '{prompt[:50]}...'")
            response = self.scraper.post(settings.CHAT_IMAGE_URL, headers=headers, json=initial_payload)
            response.raise_for_status()
            initial_data = response.json()

            image_tasks = initial_data.get("data", {}).get("images", [])
            if not image_tasks:
                raise Exception("上游 API 未返回图像任务。")

            polling_tasks = []
            for task in image_tasks[:n]:
                polling_tasks.append(self._poll_single_image(task, credential))
            
            logger.info(f"开始并发轮询 {len(polling_tasks)} 个图像任务...")
            final_urls = await asyncio.gather(*polling_tasks)

            logger.info(f"开始并发下载 {len(final_urls)} 张图片并转换为 Base64...")
            b64_tasks = [self._url_to_b64(url, credential) for url in final_urls]
            b64_results = await asyncio.gather(*b64_tasks)
            output_data = [{"b64_json": b64} for b64 in b64_results]
            logger.info("图片 Base64 转换完成，返回给客户端。")

            return {"created": int(time.time()), "data": output_data}

        except Exception as e:
            logger.error(f"图像生成流程失败: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail=f"上游服务错误: {str(e)}")

    async def _poll_single_image(self, image_task: Dict[str, Any], credential: Credential) -> str:
        url = image_task.get("url")
        prompt = image_task.get("prompt")
        if not url or not prompt:
            raise ValueError("无效的图像任务数据。")

        payload = {"prompt": prompt, "url": url}
        headers = self._prepare_image_poll_headers(credential)
        
        start_time = time.time()
        while time.time() - start_time < settings.POLLING_TIMEOUT:
            try:
                response = self.scraper.post(settings.IMAGE_GENERATOR_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                if data.get("isSuccess"):
                    relative_path = data["url"]
                    # 拼接元数据 URL，用于获取 downloadTokens
                    metadata_url = f"{settings.IMAGE_BASE_URL}{quote(relative_path, safe='')}"
                    logger.success(f"任务 {url} 成功，获取到元数据 URL: {metadata_url}")
                    return metadata_url
            except Exception as e:
                logger.warning(f"轮询任务 {url} 时出错: {e}")
            
            await asyncio.sleep(settings.POLLING_INTERVAL)
        
        raise Exception(f"轮询任务 {url} 超时。")

    async def _url_to_b64(self, metadata_url: str, credential: Credential) -> str:
        # 步骤1: 访问元数据 URL 获取 downloadTokens
        headers = {
            "Authorization": f"Firebase {credential.x_token}",
            "Origin": "https://chat.novaapp.ai",
            "Referer": "https://chat.novaapp.ai/",
            "User-Agent": USER_AGENT,
        }
        logger.info(f"正在从 {metadata_url} 获取下载令牌...")
        meta_response = await self.http_client.get(metadata_url, headers=headers)
        meta_response.raise_for_status()
        meta_data = meta_response.json()
        token = meta_data.get("downloadTokens")
        if not token:
            raise ValueError("无法从元数据中提取 downloadTokens。")
        logger.success(f"成功获取下载令牌: {token}")

        # 步骤2: 拼接最终的下载 URL 并下载图片
        final_download_url = f"{metadata_url}?alt=media&token={token}"
        logger.info(f"正在从最终 URL 下载图片: {final_download_url}")
        image_response = await self.http_client.get(final_download_url, headers=headers)
        image_response.raise_for_status()
        
        return base64.b64encode(image_response.content).decode('utf-8')

    def _prepare_chat_headers(self, credential: Credential, model_id: int) -> Dict[str, str]:
        return {
            "Accept": "text/event-stream",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://chat.novaapp.ai",
            "Referer": "https://chat.novaapp.ai/",
            "User-Agent": USER_AGENT,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x_token": credential.x_token,
            "x_user_id": credential.x_user_id,
            "x_platform": "web",
            "x_stream": "true",
            "x_pr": "true",
            "x_version": "2",
            "x_model": str(model_id),
        }

    def _prepare_image_submit_headers(self, credential: Credential, model_id: int) -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://chat.novaapp.ai",
            "Referer": "https://chat.novaapp.ai/",
            "User-Agent": USER_AGENT,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x_token": credential.x_token,
            "x_user_id": credential.x_user_id,
            "x_platform": "web",
            "x_stream": "false",
            "x_pr": "true",
            "x_model": str(model_id),
        }

    def _prepare_image_poll_headers(self, credential: Credential) -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://chat.novaapp.ai",
            "Referer": "https://chat.novaapp.ai/",
            "User-Agent": USER_AGENT,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x_token": credential.x_token,
            "x_user_id": credential.x_user_id,
            "x_platform": "web",
            "x_pr": "true",
            "x_source": "2",
        }

    def _prepare_chat_payload(self, request_data: Dict[str, Any], model_name: str) -> Tuple[Dict[str, Any], int]:
        model_id = settings.MODEL_MAPPING.get(model_name, settings.MODEL_MAPPING[settings.DEFAULT_MODEL])
        
        if 'stream_options' in request_data:
            del request_data['stream_options']

        payload = {
            "messages": request_data.get("messages", []),
            "model": model_id,
        }
        return payload, model_id

    async def get_models(self) -> JSONResponse:
        return JSONResponse(content={
            "object": "list",
            "data": [{"id": name, "object": "model", "created": int(time.time()), "owned_by": "lzA6"} for name in settings.MODEL_MAPPING.keys()]
        })

class CredentialManager:
    def __init__(self, credentials: list[Credential]):
        if not credentials:
            raise ValueError("凭证列表不能为空。")
        self.credentials = credentials
        self.lock = threading.Lock()
        self.current_index = 0

    def get_credential(self) -> Credential:
        with self.lock:
            cred = self.credentials[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.credentials)
            logger.info(f"使用凭证索引: {self.current_index}")
            return cred