# Recording provenance

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

The core `verify` command checks the bundled response fixture against selected
source judgment rows and hashes. The delivery also checked every selected source
row directly against the original downloaded Parquet file. These checks establish
exact dataset consistency, not the authenticity or correctness of original LLM
execution or human judgment.

Original pinned download:
https://huggingface.co/datasets/lmsys/mt_bench_human_judgments/resolve/f7d2896d2cc5d80f8b55c2bbc722613555233c25/data/human-00000-of-00001-25f4910818759289.parquet

For a maintenance audit, download that file outside the workshop session and run:

```sh
python3 -m scripts.verify_upstream /path/to/the/downloaded/file.parquet
```

This optional check needs a separately installed `pyarrow` reader. It verifies
the full-file SHA-256 from the manifest and every preserved source row at its
original index. Pyarrow is not required by core verification, tests, benchmarks,
routing, the wheel, or participant exercises. The check makes no network call.

The dataset declares CC BY 4.0. See THIRD_PARTY_NOTICES.md for authors, license,
selection rule and format changes. No test result is used to select recordings.
Historical GPT-3.5-Turbo/GPT-4 are source labels only. Model costs and timing
profiles in this package are workshop assumptions.
