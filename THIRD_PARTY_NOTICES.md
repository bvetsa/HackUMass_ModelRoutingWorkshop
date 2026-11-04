# Data attribution and scope

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

Selected historical prompts, model responses and human judgments derive from:
**LMSYS, MT-Bench Human Judgments**, by Lianmin Zheng, Wei-Lin Chiang, Ying Sheng,
Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li,
Eric P. Xing, Hao Zhang, Joseph E. Gonzalez and Ion Stoica, 2023.

Dataset: https://huggingface.co/datasets/lmsys/mt_bench_human_judgments

Paper: https://arxiv.org/abs/2306.05685

License declared by the dataset card: **Creative Commons Attribution 4.0**,
https://creativecommons.org/licenses/by/4.0/ . You may share and adapt the
licensed material with attribution, a license link and indication of changes.
This notice is an attribution summary, not a replacement for the license.

Pinned dataset revision: `f7d2896d2cc5d80f8b55c2bbc722613555233c25`.
The manifest records the original Parquet filename and SHA-256. The bundled
`recorded_source_rows.json` preserves selected full source rows with added
original row indices. `recorded_responses.json` extracts first-turn prompt and
response text, normalizes winner names, and groups votes by question. These
are format/selection changes. No response text has been edited. Selection takes
the first three available matching question pairs in each ten-question ID block.
The set is a 24-question convenience sample, not a representative evaluation.

Historical model labels are GPT-3.5-Turbo and GPT-4, as published. The labels
`small` and `large`, all assumed costs/service times, and all routing policies
are workshop choices. No current product claims or vendor endorsement follow.

## Handout typography

The printable handouts embed Fraunces from the official Google Fonts repository:
https://github.com/google/fonts/tree/main/ofl/fraunces . Its SIL Open Font License
is included at handouts/Fraunces-OFL.txt. Arial and Courier New are system fonts
used in the PDFs; no standalone font files are distributed here.
