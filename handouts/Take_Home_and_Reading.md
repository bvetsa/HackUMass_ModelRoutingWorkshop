# Take-home tasks and further reading

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

## Core task: a defensible routing experiment (45-60 minutes)

1. Run the tests and both evidence modes. Save their JSON/CSV reports. Identify the measured and assumed quantities in one sentence each.
2. Write 12 new authored prompts: four short difficult, four long simple and four with quoted trigger words or unfamiliar vocabulary. Keep a separate split for your final evaluation. These are educational labels, not measured LLM capability.
3. State your utility or quality floor before tuning. Change one rule or train a new small classifier using training prompts only. Choose a threshold using development prompts only.
4. Freeze the policy. Evaluate once on held-out prompts, compare against both fixed policies and random, and inspect at least two individual disagreements. If no metric changes, explain why the current dataset cannot distinguish the policies.
5. Submit a short report with evidence label, sample sizes, seed, policy version, quality, cost assumptions, measured overhead, modeled latency and one limitation. Do not report synthetic cost units as dollars saved.

Suggested deliverable: a GitHub repository containing reproducible commands, tests, data provenance, reports and a one-page explanation. Avoid committing secrets or private prompts. The supplied code folder runs locally without installation.

## Optional extensions (30-90 minutes each)

Calibration: collect representative labeled development data, plot score buckets against an appropriate empirical routing target, and explain why the naive Bayes posterior differs from answer confidence. Do not use the test set to adjust buckets or thresholds.

Cascade: add a local toy validator and count both calls when escalation occurs. Compare the same prompts under routing and cascading. Include validator overhead and all failed attempts. Label a toy validator as such.

Stress test: freeze a policy, run several synthetic seeds, and report the spread. In recorded mode, the seed changes random routing only, not the historical text or preference votes. Add a family-level split to test vocabulary generalization more strictly.

Adapter project: implement a real local inference or provider adapter if you choose. It is not required and is not included. Document costs, credentials, exact model/version, deadline, retries, token accounting and data policy. Tests should cover missing capabilities and backend failures. Offline replay remains the default demo path.

---

# Further reading

## 1. Learned routing

RouteLLM: Learning to Route LLMs with Preference Data (2024).
https://arxiv.org/abs/2406.18665
Official implementation: https://github.com/lm-sys/RouteLLM

Read for the formulation of learned routing and the need to compare response quality against cost. Ask how their preference data, training method, evaluation domains and routing overhead differ from the tiny word-count classifier here. Their published model results do not describe this package.

## 2. Cascades

FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance, Lingjiao Chen, Matei Zaharia and James Zou (2023).
https://arxiv.org/abs/2305.05176

Read for model cascades and the distinction between a pre-call choice and an escalation after an attempted answer. Ask which costs are paid even on a failed first attempt. Do not transfer historical pricing or benchmark gains to a current application.

## 3. Preference judgments

Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena, Lianmin Zheng and colleagues (2023).
https://arxiv.org/abs/2306.05685

Read for the design and limitations of model and human preference judgments. A preference win does not prove factual correctness or task completion. Ask how ordering, style and judge dependence could affect a routing evaluation.

## 4. The bundled historical recordings

LMSYS MT-Bench human judgments dataset.
https://huggingface.co/datasets/lmsys/mt_bench_human_judgments

The package pins revision f7d2896d2cc5d80f8b55c2bbc722613555233c25 and selects 24 first-turn GPT-3.5/GPT-4 question pairs. The dataset declares CC BY 4.0. Exact-source verification checks the selected text and vote transformations. Read the manifest and THIRD_PARTY_NOTICES.md before reusing or adapting it.

Sources checked for this workshop on 30 October 2026. All required commands and materials are bundled for offline use. Internet access is needed only to follow these optional reading links or retrieve the original dataset again.
