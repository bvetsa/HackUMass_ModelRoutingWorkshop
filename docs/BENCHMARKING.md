# Benchmarking and evidence

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

Read README.md and docs/WALKTHROUGH.md first. Run commands from the repository
root: the folder containing start.py.

## Implemented policies


| Policy | Decision | Limitation |
| --- | --- | --- |
| Always small / always large | One fixed model role | Quality or resource baseline |
| Random | Stable hash of prompt and seed | 50/50 baseline in expectation |
| Rules | Complexity keywords, then 180-character cutoff | Quotes, synonyms and long easy prompts break it |
| Local classifier | Multinomial naive Bayes trained on 32 authored prompts | Tiny training set, uncalibrated score, vocabulary shift |

The classifier counts word tokens and uses add-one smoothing. A large-class
posterior above the threshold selects large. A score within 0.05 of the threshold
or no known words falls back to large. That is a costlier default, **not a safety
guarantee**. The score is not a model's confidence in answer correctness.
All routers receive only `Request(prompt)`. They do not receive labels, response
text, success flags, preference votes or the evaluator's hidden synthetic state.
The seed used for the random baseline does not disclose per-model outcomes.

## Two independent evidence modes

**Synthetic:** 32 training, 12 development and 36 test prompts. An authored
`needs_large` label controls hidden response success probabilities. For small,
the pass probabilities are 0.92 on authored simple prompts and 0.26 on authored
complex prompts. For large they are 0.95 and 0.87. SHA-256 of seed, prompt and
model role produces a repeatable draw. This creates a designed teaching world,
not measured LLM performance. The evaluator holds that state. Its `PASS/FAIL`
strings are placeholders, not generated answers. Prompts share task families
across splits, so this is a weak, small educational split. The test includes
short difficult and long easy counterexamples.

**Recorded replay:** 24 first-turn question pairs from the public
[LMSYS MT-Bench human judgments dataset](https://huggingface.co/datasets/lmsys/mt_bench_human_judgments).
The exact historical GPT-3.5-Turbo and GPT-4 response text, model identities and
50 source judgment rows are bundled with CC BY 4.0 attribution. They are old
responses, not current provider performance. `verify` checks hashes and exact
transformation against the selected source rows at pinned revision
`f7d2896d2cc5d80f8b55c2bbc722613555233c25`. This is consistency/provenance
verification, not independent authentication of model execution, truth of an
answer, or endorsement of human votes. The replay accepts exact bundled prompts
only and raises on a miss. It never substitutes synthetic answers.

Recorded quality is **mean pairwise human preference credit**. For each question,
credit is the fraction of votes favoring the selected model, with ties worth
0.5. Questions have equal weight regardless of number of votes. Repeated judge
rows remain as published and are correlated. Preference is not absolute
correctness. The local classifier is trained only on the separate authored toy
training prompts, not on replay votes. Treat replay as an illustrative domain
shift, not a validated deployed router.

## Fair benchmark and overhead

All five policies see identical ordered prompt sets and identical per-model
outcomes for a given seed. Every policy gets one full warmup. Each repeated round
shuffles policy/prompt order with a seeded generator. Training and fixture loading
occur before timing. Per-request timers measure routing and dispatch separately
with `perf_counter_ns`. Each unique prompt contributes quality once, even when
timing repeats 31 times. The report includes setup time for creating the complete
router set. It excludes scoring, bootstrap, file I/O and warmup from request time.

Service latency and cost are hypothetical in **both modes**. No artificial sleep
is timed. The report adds service time analytically to measured dispatch wall
time and labels the result `modeled_e2e_ms`. This prevents replay lookup speed
from masquerading as model inference latency.

Token estimates use `ceil(characters/4)` and are not provider token counts.
Small cost units = `(estimated input tokens + 2 * estimated output tokens)/1000`.
Large uses six times those rates. Service time is 80 ms + 1 ms/output token for
small and 320 ms + 2 ms/output token for large, plus 0-40 ms deterministic jitter
in synthetic or fixed 20 ms in recorded. These are teaching assumptions, not
USD, real pricing, energy use, or historical billing. A fixed per-request cost
can favor shorter outputs, which may differ in usefulness.

Outputs are machine-readable `benchmark.json`, per-prompt `requests.csv`,
`summary.csv` and a readable `console.txt`. Summary reports quality, cost units,
large-call fraction, measured router p50/p95 and modeled end-to-end p50/p95.
The percentile uses linear interpolation. Quality delta versus always-large has
a paired percentile bootstrap interval from 1,000 resamples of unique questions.
This small-sample interval is conditional on the fixed data and synthetic seed.
It does not capture real-model stochasticity, population validity, judge bias,
or hardware timing noise. A zero interval for the baseline is mathematical.
Wall-clock timings vary across runs and machines. Data hashes, Python version
and platform accompany every JSON report.

## Experiments

```sh
python3 -m routing_workshop benchmark --split dev --threshold 0.4 --out results/dev04
python3 -m scripts.experiment
python3 -m scripts.integration_example
```

`scripts.experiment` selects one of four thresholds on development prompts using
the explicit teaching utility `quality - mean cost units`, then evaluates test
once. Change the utility only before examining the test outcome. The default
0.6 threshold was a fixed workshop choice. Do not repeatedly tune on test or
claim real cost savings from this simulator. Explore several seeds only after
freezing a policy and report the spread. In recorded mode, threshold changes
affect decisions, but seed changes cannot change historical response text.

## Repository map

`routing_workshop/routers.py` contains policies. `backends.py` separates evidence
modes and verification. `benchmark.py` handles paired evaluation. `integration.py`
is a provider-neutral callable boundary. `routing_workshop/data/` contains authored cases, public
recordings, selected source rows and the pinned manifest. `tests/` contains
functional, fairness, integrity, offline and integration tests. `docs/` contains
the integration guide and evidence notes. `scripts/` contains the threshold
experiment, offline integration example and optional source audit. `handouts/`
contains the cheat sheet, worksheet, take-home tasks and reading. Run the
commands above to check your local copy.

## Integration status

The offline integration example runs. **No live API adapter is implemented.**
Passing a model name or setting an API key does not make this package call a
provider. Read [the integration guide](INTEGRATION.md) before replacing the
offline backend. Capabilities such as retries, timeouts, budgets, privacy gates
and production monitoring require implementation and tests in your application.

Code is MIT licensed. Public replay data is separately CC BY 4.0. See
[third-party notices](../THIRD_PARTY_NOTICES.md). Workshop results make no claim of
affiliation or endorsement by model vendors, LMSYS, or the authors of RouteLLM.
