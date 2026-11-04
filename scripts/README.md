# Runnable lessons

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

Run beside start.py. The -m option lets Python find the shared package.

| Order | Command | File | Purpose |
| --- | --- | --- | --- |
| First | python3 start.py | [start.py](../start.py) | Trace one rule decision |
| Next | python3 -m scripts.compare_routers | [compare_routers.py](compare_routers.py) | Compare rule/learned decisions |
| Then | python3 -m scripts.integration_example | [integration_example.py](integration_example.py) | Call one function and return historical text |
| Experiment | python3 -m scripts.experiment | [experiment.py](experiment.py) | Select on development, then evaluate test |

Use [the walkthrough](../docs/WALKTHROUGH.md) for unfamiliar Python concepts.
The first three commands write no result files. The experiment writes
results/experiment/ and reveals test results; choose the objective first.

## Optional maintenance audit

[verify_upstream.py](verify_upstream.py) checks a separately downloaded original
dataset. It is outside the beginner path and needs optional pyarrow.
Ordinary verification, lessons, tests and benchmarks need only the standard
library and bundled files. See [DATA.md](../docs/DATA.md).
