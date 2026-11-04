# Experiment worksheet

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

Name or pair (optional): ____________________   Date: _______________

## 1. Prediction before results

For each prompt, predict what the implemented rules do and what you would prefer. Keep those answers separate.

| Prompt | Rule prediction | Your preferred route and reason |
| --- | --- | --- |
| Extract an email from a long event note | __________ | __________________________ |
| Prove it. | __________ | __________________________ |
| Translate the word prove into French | __________ | __________________________ |

## 2. Objective before tuning

My quality metric: _______________________________________________

My quality floor or utility formula: _______________________________

Why this objective suits the application: __________________________

The supplied script uses synthetic pass rate minus mean assumed cost units. You may choose another objective, but state it before looking at test.

## 3. Development experiment

Use 12 DEV prompts, never the test prompts, to choose a threshold. From the code folder: python3 -m scripts.experiment. The script uses the teaching utility above. For your own objective, use the CLI on DEV and calculate your stated rule.

| Threshold | DEV quality | Cost units | Router p95 ms | Objective value |
| --- | --- | --- | --- | --- |
| 0.2 | ______ | ______ | ______ | ______ |
| 0.4 | ______ | ______ | ______ | ______ |
| 0.6 | ______ | ______ | ______ | ______ |
| 0.8 | ______ | ______ | ______ | ______ |

My frozen threshold: ______   Reason: _____________________________

STOP: freeze your choice before the next page. Similar or tied outcomes are a valid finding on a small set.

---

# Experiment worksheet: evaluation

## 4. Held-out test

Evaluate the frozen choice once on 36 TEST prompts. Run the benchmark with --threshold followed by your chosen number and --out results/my-test. Compare with always-large on identical questions.

| Metric | Always large | Frozen policy |
| --- | --- | --- |
| Synthetic pass rate | __________ | __________ |
| Mean assumed cost units | __________ | __________ |
| Measured router p95 ms | __________ | __________ |
| Modeled end-to-end p95 ms | __________ | __________ |

Paired quality difference and conditional bootstrap interval: __________

One failure example from requests.csv: ______________________________

Is it a selection error or an answer failure after an appropriate route?

_________________________________________________________________

## 5. Historical replay as a separate experiment

Run recorded mode with the frozen threshold. Record quality as human pairwise preference credit. Do not compare this percentage numerically with synthetic pass rate.

Always-large credit: ______   Frozen-policy credit: ______

One reason this differs from the synthetic teaching world: ___________

_________________________________________________________________

## 6. Claim and limitation

Write one sentence your evidence supports, with the mode and sample size:

_________________________________________________________________

_________________________________________________________________

Write one conclusion these results cannot establish:

_________________________________________________________________

Evidence checklist: objective written first; policy frozen before test; paired prompts; unique-question sample count; overhead included; hypothetical costs labeled; historical preference separated from correctness.
