# Qwen3.8-Flash-Next

This is the qualified Qwen3.8-Flash-Next (Qwen4Exp) pack I use with B70 LLM Controller. It contains one served checkpoint — weights, tokenizer, and the 102.4 GB PLE n-gram table together in a single pinned revision — a frozen unified runtime, and the exact B70 configurations that passed testing. Both modes, Base and MTP3, run on the same single runtime image and differ only by launch configuration.

## Models

| Variant | Repository | Revision |
| --- | --- | --- |
| W4A16 | `devan-carlin/Qwen3.8-Flash-Next-W4A16` | `40b8f18df4d4a32cb6e687a51c78207e5e438522` |

The repository is ungated and public. The pinned revision is 31 files, 179,841,735,233 bytes total (≈ 180 GB) — `ple_table_qwen4exp.pt` alone is 102,400,493,290 bytes and **is part of the revision**, so the download covers everything the runtime needs. `b70ctl` downloads the exact revision above and checks it against the 31-file inventory in `pack.json`; plan for the full ≈ 180 GB on first install.

## Modes

- **Base** serves the checkpoint without speculative decoding (util 0.85). The MTP drafter never loads in this mode.
- **MTP3** enables multi-token-prediction speculative decoding at exactly depth 3 (`{"method":"mtp","num_speculative_tokens":3}`, util 0.91): each proposal drafts exactly 3 tokens and the target verifies 4 rows. The mode display is `MTP3` — the depth is part of the contract; MTP1 exists in the runtime as a capability but is not a pack mode.

Mode availability depends on card count and context; a mode only appears when that exact combination has a profile.

## Hardware and context support

| Checkpoint | Cards / TP | Qualified contexts and modes |
| --- | --- | --- |
| W4A16 | 4 | 32K, 64K, 128K, 256K: Base, MTP3 |

TP4 on 4× Arc Pro B70 is the only topology this pack publishes. No sub-TP4 lane was ever qualified for this checkpoint (the W4A16 GEMM K≥6144 race is TP1/TP2-reachable), so no such profile exists.

Context ladder law: each mode was qualified at its maximum context — 262144 — on the identical runtime contract, and that qualification covers every lower tier the pack publishes (32K/64K/128K are data-only context ceilings; they require no separate boot). The native `max_position_embeddings` of the checkpoint is 262,144.

Only combinations that passed qualification are included. `b70ctl` reads the exact 8-profile matrix from `pack.json`, so unsupported combinations simply do not appear.

## Hard runtime requirements (baked into the image)

These are properties of the pinned runtime image, not options: pinned-host PLE table (2-slab UVA load, zero device residency — `PLE_TABLE_PATH` resolves into the read-only model mount), the B70 Level-Zero peer-residency shim (`LD_PRELOAD`), TP4 + expert parallelism, W4A16 bf16 serving, breakable FULL_AND_PIECEWISE XPU graphs `[1,2,4,8,256]` at `--max-num-batched-tokens 256` / `--max-num-seqs 4` (torch.compile mode NONE), automatic prefix caching ON with the ALIGN Mamba cache mode, and the dense-QSA serve configuration.

Dense QSA is a correctness requirement for this checkpoint: the pinned config ships five `text_config.indexer_*` keys but the checkpoint contains no indexer weights, so the runtime image carries the patched serving config (the pinned config minus exactly those five keys, sha256 `91fa33ca…`) and its entrypoint rebuilds the serve directory inside the container at boot (`/work/flashnext-serve`) from the read-only Controller model mount. The mounted snapshot is never written.

Vision is qualified (image modality, `{"image":2,"video":0}`); **video is not qualified** and stays at 0.

## Performance

Retained qualified results from the promoted unified runtime (BetterBench v0.6.0, 32K contract, temperature 0.7, single stream unless noted), not new measurements. Test host: 4× Intel Arc Pro B70 32 GB.

| Quantity | Base | MTP3 |
| --- | ---: | ---: |
| Combined weighted decode | 58.34 tok/s | 119.86 tok/s |
| Prefill @ ≈23.6K-token prompts | 2476 tok/s | 2290 tok/s |
| TTFT p50 (shorts) | 107.5 ms | 123.0 ms |
| Concurrency C4 aggregate | 183.7 tok/s | 138.3 tok/s |

Where each mode wins: MTP3 wins every single-stream decode category (+69% to +155%) and C1/C2 aggregates (2.00×/1.82×); Base wins prefill throughput at every depth (+7.3–8.5%), TTFT at every depth/level, and C4 aggregate (+32.7%). The two modes are complementary rather than overlapping. Concurrency numbers are recorded envelope data only — concurrency tuning is explicitly deferred (the `max_num_seqs 4` contract is unchanged from qualification).

## Runtime

The pack uses this single qualified runtime — one image for all 8 profiles and both modes:

```text
ghcr.io/wu1ff/qwen38-flashnext-b70@sha256:85512b52c09fa660a2e7fe441417129e7c47fac727fd85f66ccea6b65e0a9122
```

This is the 2026-09-27 packaging layer (serve preparator + patched config + entrypoint) on top of the unified runtime authority that serves Base (speculation off) and MTP3 (depth 3) from one image — including the GDN convolution state-index 64-bit correctness correction that fixed the deep-prefill DEVICE_LOST failure mode. No separate Base or MTP3 runtime image exists or is referenced.

If the image is missing, `b70ctl` pulls that immutable reference and verifies that Docker reports the expected image ID before offering any profile that uses it. On Docker daemons using the containerd image store, the image ID equals the registry manifest digest recorded in `pack.json`, and verification succeeds; a classic-graphdriver daemon reports the config digest instead, which would not match. This pack targets the containerd image-store daemon class, same as the existing packs.

The runtime mounts the B70 devices (`/dev/dri`) plus one fixed read-only bind of `/dev/dri/by-path` so serving resolves cards by their stable device paths. That exact bind is the only host mount the pack is allowed to request; `b70ctl` rejects any other pack-controlled mount. All caches live inside the container (`/work/*`).

## Runtime recipe

For the runtime build history, compatibility work, qualified launch contract, and technical provenance, see [RUNTIME_RECIPE.md](RUNTIME_RECIPE.md).

## Using the pack

Install from the public catalog via **Model Packs → Browse Available Packs**, or import this pack directory with **Model Packs → Import Local Pack** while working from the source tree. There is one target checkpoint; preparing it is the ≈ 180 GB download. Existing exact model revisions and the runtime are reused on update.

Then open **Run Model**, choose the checkpoint, and select from the card, context, and mode values shown. Choose Local or LAN access, set the port, and start it. First boot takes roughly six minutes to readiness.

`pack.json` is intentionally readable if you want to inspect all 8 profiles, the model file inventory, and launch data yourself.

## Licenses

The Controller's MIT license does not relicense the model weights, runtime components, or other third-party software. Check the upstream terms for each repository and component you use.
