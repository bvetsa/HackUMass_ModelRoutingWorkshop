# Learn model routing

A **router** chooses which model should handle a prompt before asking for an
answer. Learn that decision through a few Python rules and a small classifier
whose implementation you can read.

**Start here even if you have never read routing code.** Everything needed is
inside this repository. You do not need the slides, a presenter, an API key,
a GPU, a model download or a paid service. This program does not run an LLM:
small/large are model roles in an offline teaching example.

## 1. Run your first example

You need **Python 3.10 or newer**. Download and extract the repository if you
have a ZIP. Open a terminal in the folder containing this README and
[start.py](start.py), rather than inside routing_workshop/.

On macOS/Linux:

~~~sh
python3 --version
python3 start.py
~~~

On Windows:

~~~powershell
py --version
py start.py
~~~

In later commands, replace python3 with py on Windows, or with python if that
is your Python 3 command. No pip install is needed.

You should see:

~~~text
Prompt: Extract the email from Contact: ada@example.org.
Selected role: small
Reason: short prompt without trigger
Routing chooses a role. It does not generate an answer.
~~~

Open start.py. Its five numbered steps run from top to bottom. Change the
prompt to "Prove it.", predict the role, then run it again. Next, follow the
route() method in [routers.py](routing_workshop/routers.py).

## 2. Follow this reading order

| Step | Read / run | What you will understand |
| --- | --- | --- |
| 1 | [start.py](start.py) | Prompt in, decision out |
| 2 | [Python primer and walkthrough](docs/WALKTHROUGH.md) | Variables, objects, function calls and the full trace |
| 3 | [RuleRouter in routers.py](routing_workshop/routers.py) | Three if/return branches |
| 4 | [compare_routers.py](scripts/compare_routers.py) | Learning a decision from training examples |
| 5 | [integration.py](routing_workshop/integration.py) and [its example](scripts/integration_example.py) | Calling one chosen answer function |
| 6 | [Exercises](docs/EXERCISES.md) | Predict, change, test and explain |
| Later | [Benchmarking](docs/BENCHMARKING.md) | Compare policies without overstating evidence |

Run the second lesson:

~~~sh
python3 -m scripts.compare_routers
~~~

Here, -m means "run this Python module." Stay in the same folder as start.py so
Python can find both scripts/ and routing_workshop/.

## 3. Know where things live

~~~text
start.py                   First program to read and edit
routing_workshop/
  routers.py               Choose a role: rules, classifier and baselines
  integration.py           Call the function for the chosen role
  backends.py              Simulate outcomes or replay historical text
  benchmark.py             Compare policies; read after the basics
  __main__.py              Optional terminal-command interface
  data/                    All training examples and recorded data
scripts/                   Runnable lessons and experiments
docs/                      Walkthrough, exercises and deeper explanations
handouts/                  Printable and editable workshop sheets
tests/                     Checks that routing/evaluation still work
pyproject.toml             Optional installation metadata; skip initially
~~~

The files under routing_workshop/ are the actual implementation, not another
copy of the examples. __init__.py files mark/import Python packages.

## 4. Check the code and try evaluation

~~~sh
python3 -m unittest discover -s tests -v
python3 -m routing_workshop verify
python3 -m routing_workshop route "Prove it." --policy local
python3 -m routing_workshop benchmark --mode synthetic --out results/synthetic
python3 -m routing_workshop benchmark --mode recorded --out results/recorded
~~~

Reports are created in results/ in this repository. Open console.txt for a
readable table or requests.csv to inspect individual questions.

**Two different evidence modes:** synthetic mode uses designed PASS/FAIL
outcomes, not measured LLM quality. Recorded mode replays 24 historical
response pairs and scores human preference, not correctness. In both modes,
service time and cost units are assumptions; local router/dispatch overhead
is measured. No live API adapter is included.

## If something goes wrong

| Symptom | What to check |
| --- | --- |
| Python command not found | Try the other command above; otherwise install Python 3.10+ first |
| Python version below 3.10 | Use a newer Python before continuing |
| Cannot open start.py / module not found | Open the terminal beside start.py and this README |
| Replay rejects a custom prompt | Expected: replay knows exact bundled prompts only; use start.py or the route command for arbitrary routing |
| No answer appears after routing | Expected: choosing a role and generating an answer are separate steps |

More material: [handouts](handouts/), [integration guide](docs/INTEGRATION.md),
[data provenance](docs/DATA.md), and [script descriptions](scripts/README.md).

Code: [MIT license](LICENSE). Historical data: separately CC BY 4.0;
see [attribution and notices](THIRD_PARTY_NOTICES.md).
