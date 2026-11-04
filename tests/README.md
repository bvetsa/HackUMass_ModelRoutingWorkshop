# What the tests protect

Run from the folder containing start.py:

    python3 -m unittest discover -s tests -v

Python discovers files named test_*.py. Each test_* method checks one promise.
assertEqual(actual, expected) fails if values differ; assertRaises checks that
an invalid operation produces the expected error. An error/failure tells you
which promise to inspect. OK means these checks passed, not that routing works
well on every real task.

| File | Checks |
| --- | --- |
| test_routers.py | Prompt-only inputs, rule boundaries, training and fallbacks |
| test_backends.py | Repeatable outcomes, exact replay, integrity and one-call dispatch |
| test_benchmark.py | Same questions, no quality double-counting, timing and reports |
| test_examples.py | The beginner programs documented in the README |

After intentionally changing a rule, inspect its affected tests. Decide the new
behavior first; do not delete a failing check just to get OK.
