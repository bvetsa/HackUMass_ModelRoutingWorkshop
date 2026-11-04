"""Translate terminal commands into ordinary Python function calls.

Python runs this file for: python3 -m routing_workshop ...
Read start.py first; this file handles the optional command-line interface.
"""

import argparse
from dataclasses import asdict
import json

from .backends import DATA, verify_recordings
from .benchmark import policies, run_benchmark, write_report
from .routers import Request


def main():
    parser = argparse.ArgumentParser(
        description="Offline routing workshop. No API keys, downloads, or model inference."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    route_parser = commands.add_parser(
        "route", help="Route prompt text; do not generate an answer"
    )
    route_parser.add_argument("prompt")
    route_parser.add_argument("--policy", choices=["rules", "local"], default="rules")
    route_parser.add_argument("--threshold", type=float, default=0.6)

    benchmark_parser = commands.add_parser(
        "benchmark", help="Compare five policies offline"
    )
    benchmark_parser.add_argument(
        "--mode", choices=["synthetic", "recorded"], default="synthetic"
    )
    benchmark_parser.add_argument("--split", choices=["dev", "test"], default="test")
    benchmark_parser.add_argument("--seed", type=int, default=7)
    benchmark_parser.add_argument("--repeats", type=int, default=31)
    benchmark_parser.add_argument("--threshold", type=float, default=0.6)
    benchmark_parser.add_argument("--out", default="results/latest")

    commands.add_parser(
        "verify", help="Check bundled recordings against source rows and hashes"
    )
    args = parser.parse_args()

    try:
        if args.command == "route":
            # Use the exact same training/configuration as the benchmark.
            router = policies(threshold=args.threshold)[args.policy]
            decision = router.route(Request(args.prompt))
            print(json.dumps(asdict(decision), indent=2))

        elif args.command == "verify":
            if not DATA.joinpath("recorded_source_rows.json").is_file():
                raise ValueError("Replay fixtures are absent in the public edition. Run the synthetic benchmark instead.")
            verification = verify_recordings()
            print(json.dumps(verification, indent=2))

        else:
            report = run_benchmark(
                mode=args.mode,
                split=args.split,
                seed=args.seed,
                repeats=args.repeats,
                threshold=args.threshold,
            )
            print(write_report(report, args.out))

    except (ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
