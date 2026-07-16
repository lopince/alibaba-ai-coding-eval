ARG VLLM_IMAGE=vllm/vllm-openai-cpu:latest-arm64
FROM ${VLLM_IMAGE}

# Install the benchmark extra's dependencies directly. The ARM CPU package has
# a local `+cpu` version that package indexes cannot resolve as `vllm[bench]`.
RUN uv pip install --system --break-system-packages \
    pandas matplotlib seaborn datasets scipy plotly

ENTRYPOINT ["vllm"]
