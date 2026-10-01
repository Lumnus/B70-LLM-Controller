# Build the B70 residency shim

Inside the pinned `vllm/vllm-openai-xpu` v0.30.0 amd64 parent image (GCC 13.3, Level Zero 1.28.2 headers), compile the retained source with:

```sh
gcc -std=c11 -O2 -fPIC -shared -Wall -Wextra -Werror \
  -o libl0_peer_residency_shim.so l0_peer_residency_shim.c \
  -lze_loader -ldl -pthread
```

Install the output as `/opt/b70-residency-shim/libl0_peer_residency_shim.so` and preload it with `LD_PRELOAD` as in the production launch. Retained source SHA-256: `f79e1bbaa18a9c29ac621452dd091c6522f2802d96c51a95ca9cb63f1ee1f10c`. Production binary SHA-256: `ae2c82f549d97393268cbd7b90dba7cf38fd00dbccae54f090b1a545e5613b3c`.
