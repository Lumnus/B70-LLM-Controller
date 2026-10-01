# Qwen3.8-Flash-Next B70 pack runtime — packaging layer ONLY.
# Parent is the unified runtime authority (Base spec-off + MTP3 depth-3).
# This layer adds no runtime/framework bytes: one patched serving config,
# one deterministic serve-directory preparator, and the pack entrypoint.
FROM local/qwen38-flashnext-v030:runtime-authority@sha256:ad6d44d7a8aee41a4d419befbcaf78c7d73e0acd7f7aaaf597b5ff283601b448
COPY serve-config.json /opt/b70-flashnext/serve-config.json
COPY prepare-serve.sh /opt/b70-flashnext/prepare-serve.sh
RUN chmod 0755 /opt/b70-flashnext/prepare-serve.sh && mkdir -p /work
ENTRYPOINT ["/opt/b70-flashnext/prepare-serve.sh"]
