#!/bin/bash
# Teammate A runs this on Instance A (Ubuntu AMD cloud)
# Starts Gemma 4 12B via vLLM ROCm on Port 9000

if [ -z "" ]; then
    echo "ERROR: HF_TOKEN is not set."
    echo "Run: export HF_TOKEN=hf_your_token_here"
    exit 1
fi

echo "Starting Gemma 4 12B via vLLM ROCm..."
echo "This will take 3-5 minutes to load the model."
echo ""

docker run -d \
    --name cardiocore_vllm \
    --device /dev/kfd \
    --device /dev/dri \
    --group-add video \
    --ipc host \
    --shm-size 16g \
    -p 9000:8000 \
    -e HF_TOKEN= \
    -e HSA_OVERRIDE_GFX_VERSION=9.4.2 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    vllm/vllm-openai-rocm:latest \
    --model google/gemma-4-12b-it \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.85 \
    --limit-mm-per-prompt image=8

echo ""
echo "Container started. Check logs with:"
echo "  docker logs cardiocore_vllm --tail 30"
echo ""
echo "Once loaded, test with:"
echo "  curl http://localhost:9000/v1/models"
