#!/usr/bin/env bash
set -euo pipefail
GDN_BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GDN_PARENT=local/qwen38-flashnext-v030:mtp3-c1
GDN_EXPECTED=sha256:3bc0ee337a732b9341f1653264a0672b7661bcf37c926dc3cda404a1c02d5656
[[ "$(docker image inspect "$GDN_PARENT" --format '{{.Id}}')" == "$GDN_EXPECTED" ]]
docker run --rm --name flashnext-gdn-build --entrypoint /bin/bash --network none \
  --mount type=bind,src="$GDN_BUILD_DIR",dst=/build \
  --mount type=bind,src="$GDN_BUILD_DIR/toolchain",dst=/toolchain,readonly \
  "$GDN_PARENT" /build/build.sh
