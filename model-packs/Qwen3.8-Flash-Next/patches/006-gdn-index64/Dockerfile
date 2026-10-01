ARG PARENT=local/qwen38-flashnext-v030:mtp3-c1
FROM ${PARENT}
COPY libgdn_index64.so /opt/venv/lib/python3.12/site-packages/vllm_xpu_kernels/libgdn_index64.so
COPY overlay/vllm/_xpu_ops.py /opt/venv/lib/python3.12/site-packages/vllm/_xpu_ops.py
COPY overlay/vllm/_xpu_ops.py /workspace/vllm/vllm/_xpu_ops.py
RUN /opt/venv/bin/python -c 'import torch, vllm_xpu_kernels; from pathlib import Path; torch.ops.load_library(str(Path(vllm_xpu_kernels.__file__).with_name("libgdn_index64.so"))); print(torch.ops._gdn_index64.gdn_attention.default._schema)'
