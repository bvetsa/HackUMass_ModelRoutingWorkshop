# Small changes, one at a time

Run commands beside start.py. Keep an original copy before experimenting.
Printable sheets and take-home tasks are in [handouts/](../handouts/).

## 1. Predict three rule decisions

Change only the prompt in start.py. Predict before each run:

- A short email-extraction request.
- "Prove it."
- "Translate the word prove into French."

Run python3 start.py. Find the exact if/return in RuleRouter.route().
Separate predicting the implementation from choosing an appropriate real model.

## 2. Change one setting

Change RuleRouter() in start.py to RuleRouter(max_chars=30). Try prompts of
exactly 30 and 31 characters without trigger words. What does strict
greater-than mean? Try a long, easy extraction task. Why can length mislead?

Restore defaults before continuing.

## 3. Follow a learned route

~~~sh
python3 -m scripts.compare_routers
~~~

Trace training -> LocalRouter -> score -> Decision. Find the line excluding
development/test data from training. Change a displayed prompt to unfamiliar
words. Explain the missing-score fallback. Change threshold and predict which
examples might change. The score is not answer confidence.

## 4. Trace one backend call

~~~sh
python3 -m scripts.integration_example
~~~

Find the prompt, small_backend(), large_backend() and route_and_call().
Which function runs? What does it return? Why does a new arbitrary prompt fail?

## 5. Write an objective before tuning

Use DEVELOPMENT data to choose settings:

~~~sh
python3 -m routing_workshop benchmark --split dev --threshold 0.4 --out results/dev04
~~~

Inspect requests.csv and summary.csv in that output folder. Record mode,
sample size, quality definition, assumed costs and measured overhead.

The next script uses the supplied objective to select on development data,
then immediately evaluates held-out test data:

~~~sh
python3 -m scripts.experiment
~~~

Choose a custom objective before running this script or looking at test.
Tied or unchanged decisions are a valid finding on a tiny dataset.

## 6. State an honest result

After freezing a policy:

~~~sh
python3 -m routing_workshop benchmark --mode synthetic --out results/my-synthetic
~~~

Why does synthetic pass rate depend on the designed outcomes?
Which timing values are measured/assumed? Name a conclusion these results cannot
establish about a deployed system.

## Check your changes

~~~sh
python3 -m unittest discover -s tests -v
~~~

Tests check particular promises, not usefulness on every task. If intentionally
changing a rule, inspect affected expectations after choosing the new behavior.
