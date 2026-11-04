"""Choose a threshold on development data, then evaluate held-out test data.

Run: python3 -m scripts.experiment
Write down your objective first: this script also reveals test results.
"""

import json
from pathlib import Path

from routing_workshop.benchmark import run_benchmark, write_report


def main():
    development_rows = []

    # Try four settings on DEVELOPMENT data. Leave test data alone for now.
    for threshold in [0.2, 0.4, 0.6, 0.8]:
        report = run_benchmark(split="dev", threshold=threshold, repeats=11)
        local_result = next(
            row for row in report["summary"] if row["policy"] == "local"
        )

        # This teaching objective uses an explicit, arbitrary cost weight.
        utility = local_result["quality"] - local_result["mean_cost_units"]
        development_rows.append(
            {"threshold": threshold, "utility": utility, **local_result}
        )

    # max() keeps the first setting on a tie. Freeze the choice before test.
    best_row = max(development_rows, key=lambda row: row["utility"])
    best_threshold = best_row["threshold"]

    output_folder = Path("results/experiment")
    output_folder.mkdir(parents=True, exist_ok=True)
    (output_folder / "dev-sweep.json").write_text(
        json.dumps(development_rows, indent=2) + "\n", encoding="utf-8"
    )

    print(
        "Selected threshold on dev:", best_threshold,
        "utility = quality - mean cost units",
    )
    test_report = run_benchmark(threshold=best_threshold, repeats=31)
    print(write_report(test_report, output_folder / "test"))


if __name__ == "__main__":
    main()
