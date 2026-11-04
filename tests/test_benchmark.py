"""Fair comparisons, timing accounting, report files and command-line use."""

import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from routing_workshop.benchmark import (
    paired_interval,
    percentile,
    run_benchmark,
    write_report,
)


class BenchmarkTests(unittest.TestCase):
    def test_percentiles_and_paired_interval(self):
        self.assertEqual(percentile([1, 3], 0.5), 2)
        self.assertEqual(paired_interval([0, 1], [0, 1]), [0, 0])
        with self.assertRaises(ValueError):
            paired_interval([1], [])

    def test_fair_pairing_and_overhead_accounting(self):
        report = run_benchmark(repeats=2)
        self.assertEqual(len(report["rows"]), 36 * 5)
        for row in report["rows"]:
            self.assertGreaterEqual(row["local_dispatch_ms"], row["router_ms"])
            self.assertAlmostEqual(
                row["modeled_e2e_ms"],
                row["service_ms"] + row["local_dispatch_ms"],
            )
        self.assertTrue(all(row["n"] == 36 for row in report["summary"]))

        reference_ids = [
            row["id"] for row in report["rows"] if row["policy"] == "rules"
        ]
        for policy in ["always_small", "always_large", "random", "rules", "local"]:
            ids = [row["id"] for row in report["rows"] if row["policy"] == policy]
            self.assertEqual(ids, reference_ids)

    def test_repeats_do_not_inflate_quality_sample(self):
        first = run_benchmark(repeats=1)
        repeated = run_benchmark(repeats=3)
        for first_row, repeated_row in zip(first["rows"], repeated["rows"]):
            for key in ["id", "model", "quality", "cost_units", "service_ms"]:
                self.assertEqual(first_row[key], repeated_row[key])

    def test_seed_changes_outcomes_not_rules(self):
        first = run_benchmark(seed=7, repeats=1)
        second = run_benchmark(seed=9, repeats=1)
        self.assertNotEqual(
            [row["quality"] for row in first["rows"]],
            [row["quality"] for row in second["rows"]],
        )
        first_routes = [
            row["model"] for row in first["rows"] if row["policy"] == "rules"
        ]
        second_routes = [
            row["model"] for row in second["rows"] if row["policy"] == "rules"
        ]
        self.assertEqual(first_routes, second_routes)

    def test_no_network_required(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            report = run_benchmark(mode="synthetic", repeats=1)
            self.assertEqual(len(report["rows"]), 36 * 5)

    def test_report_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_benchmark(repeats=1)
            text = write_report(report, directory)
            self.assertIn("SYNTHETIC", text)
            path = Path(directory)
            saved_report = json.loads((path / "benchmark.json").read_text())
            self.assertEqual(saved_report["seed"], 7)
            self.assertEqual(
                len((path / "requests.csv").read_text().splitlines()), 181
            )

    def test_bad_benchmark_config(self):
        for settings in [
            {"repeats": 0},
            {"mode": "live"},
            {"split": "train"},
        ]:
            with self.assertRaises(ValueError):
                run_benchmark(**settings)

    def test_cli(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "routing_workshop",
                "route", "Prove this", "--policy", "rules",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["model"], "large")
