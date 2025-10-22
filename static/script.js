document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('api-key');
    const ratioSelect = document.getElementById('ratio-select');
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const countSlider = document.getElementById('count-slider');
    const countValue = document.getElementById('count-value');
    const imageGrid = document.getElementById('image-grid');
    const spinner = document.getElementById('spinner');
    const errorMessage = document.getElementById('error-message');
    const placeholder = document.getElementById('placeholder');

    async function handleGenerate() {
        const apiKey = apiKeyInput.value.trim();
        const prompt = promptInput.value.trim();

        if (!apiKey || !prompt) {
            showError("请确保 API Key 和提示词都已填写。");
            return;
        }

        setLoading(true);

        // 注意：虽然我们在这里请求 b64_json，但后端已被修改为总是返回 b64_json
        const payload = {
            model: "nova-dalle3",
            prompt: prompt,
            n: parseInt(countSlider.value, 10),
            size: ratioSelect.value,
            response_format: "b64_json" 
        };

        try {
            const response = await fetch('/v1/images/generations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || '生成失败，未知错误。');
            }

            if (result.data && result.data.length > 0) {
                displayImages(result.data);
            } else {
                throw new Error('API 返回了成功状态，但没有图片数据。');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    }

    function displayImages(data) {
        imageGrid.innerHTML = '';
        data.forEach(item => {
            // --- 核心修改点 ---
            // 检查 item.b64_json 而不是 item.url
            if (item.b64_json) {
                const imgContainer = document.createElement('div');
                imgContainer.className = 'image-container';
                const img = document.createElement('img');
                // 使用 Data URL 格式来显示 Base64 图片
                img.src = 'data:image/jpeg;base64,' + item.b64_json;
                img.alt = 'Generated Image';
                imgContainer.appendChild(img);
                imageGrid.appendChild(imgContainer);
            }
        });
    }

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        spinner.classList.toggle('hidden', !isLoading);
        placeholder.classList.toggle('hidden', isLoading || imageGrid.children.length > 0);
        if (isLoading) {
            imageGrid.innerHTML = '';
            hideError();
        }
    }

    function showError(message) {
        errorMessage.textContent = `错误: ${message}`;
        errorMessage.classList.remove('hidden');
        imageGrid.innerHTML = '';
        placeholder.classList.add('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    countSlider.addEventListener('input', () => countValue.textContent = countSlider.value);
    generateBtn.addEventListener('click', handleGenerate);
});