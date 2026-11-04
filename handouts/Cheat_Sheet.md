# Model routing: one-page cheat sheet

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

## The decision

Filter by capabilities and policy, then choose a model before generation. A route is useful only under a stated quality requirement, cost objective and latency budget. A cascade may make multiple calls and must count every attempt.

## Implemented offline policies

Rules: complexity keyword, then length >180 characters, otherwise small.
Local: word-count naive Bayes trained on 32 authored prompts. Default large-class threshold: 0.6. An ambiguity band of +/-0.05 or zero known words selects large. The score is not answer confidence. Both receive prompt text only.

## Run from the code folder

```sh
python3 -m unittest discover -s tests -v
python3 -m routing_workshop verify
python3 -m routing_workshop route "Prove it." --policy local
python3 -m routing_workshop benchmark --mode synthetic
python3 -m routing_workshop benchmark --mode recorded
python3 -m scripts.experiment
```

## Evidence labels

SYNTHETIC: designed hidden success outcomes, no LLM inference. 32 train / 12 dev / 36 test prompts. Freeze choices on dev before test.
RECORDED REPLAY: 24 historical MT-Bench response pairs with exact-source checks. Quality is human pairwise preference credit, ties = half. It is not accuracy or current model performance.
In BOTH modes, service time and cost units are assumptions. Only local router/dispatch overhead is measured. No live API adapter ships.

## A fair report

Use identical prompts and per-model outcomes for fixed, random and learned policies. Count each unique question once for quality. Include routing, dispatch and service in end-to-end time. Report p50/p95, quality, assumed or actual cost, failure examples and uncertainty limits. Replay lookup time is not inference latency.

## One experiment to take home

Write an objective. Add short difficult, long simple and quoted-keyword cases. Split before tuning. Freeze the policy, evaluate once, inspect errors and state what the evidence cannot establish.

Python 3.10+ only. No keys, GPU, model download or paid API required. See README.md for commands and handouts/ for the worksheet and take-home tasks.
