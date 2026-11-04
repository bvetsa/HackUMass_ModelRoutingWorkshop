"""Compare policies fairly. This is the advanced evaluation lesson.

run_benchmark() follows numbered phases: load, configure, warm up, time,
make per-question rows, summarize, attach evidence. It never runs an LLM.
"""

import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import sys
import time

from .backends import DATA, Outcome, RecordedBackend, SyntheticBackend, read_data
from .routers import (
    Decision,
    FixedRouter,
    LocalRouter,
    RandomRouter,
    Request,
    RuleRouter,
)


@dataclass
class TimingSample:
    """One repetition. Named fields keep the timing loop easy to follow."""

    router_ms: float
    local_dispatch_ms: float
    decision: Decision
    outcome: Outcome


def percentile(values, q):
    """Sort numbers and interpolate; q=0.95 asks for the 95th percentile."""
    if not values:
        raise ValueError("no values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def paired_interval(a, b, seed=7, reps=1000):
    """Bootstrap per-question quality differences, preserving question pairs.

    This interval is conditional on the fixed dataset/seed, not a guarantee
    about new users, real inference, judge bias or population performance.
    """
    if len(a) != len(b) or not a:
        raise ValueError("paired non-empty vectors required")

    generator = random.Random(seed)
    differences = [first - second for first, second in zip(a, b)]
    question_count = len(differences)
    resampled_means = []
    for _ in range(reps):
        sampled = [
            differences[generator.randrange(question_count)]
            for _ in range(question_count)
        ]
        resampled_means.append(sum(sampled) / question_count)
    return [
        percentile(resampled_means, 0.025),
        percentile(resampled_means, 0.975),
    ]


def policies(seed=7, threshold=0.6):
    """Build the same five policies used by the CLI and every benchmark."""
    training = []
    for case in read_data("synthetic_cases.json"):
        if case["split"] == "train":
            training.append((case["prompt"], case["needs_large"]))

    return {
        "always_small": FixedRouter("small"),
        "always_large": FixedRouter("large"),
        "random": RandomRouter(seed),
        "rules": RuleRouter(),
        "local": LocalRouter(training, threshold=threshold),
    }


def run_benchmark(
    mode="synthetic", split="test", seed=7, repeats=31, threshold=0.6
):
    """Return a report dictionary; write_report() saves it separately."""
    if mode not in ("synthetic", "recorded"):
        raise ValueError("unknown mode")
    if split not in ("dev", "test"):
        raise ValueError("choose dev or test")
    if repeats < 1:
        raise ValueError("repeats must be positive")

    # 1. Load one evaluation set/backend shared by all five policies.
    all_cases = read_data("synthetic_cases.json")
    if mode == "synthetic":
        cases = [case for case in all_cases if case["split"] == split]
        backend = SyntheticBackend(cases, seed)
    else:
        cases = read_data("recorded_responses.json")
        backend = RecordedBackend()

    # 2. Create/train policies before request timing; report setup separately.
    setup_start = time.perf_counter_ns()
    routers = policies(seed, threshold)
    setup_ms = (time.perf_counter_ns() - setup_start) / 1e6
    requests = [Request(case["prompt"]) for case in cases]

    # 3. Give every policy one full warmup. Routers receive prompt text only.
    for router in routers.values():
        for request in requests:
            decision = router.route(request)
            backend.respond(request, decision.model)

    # 4. Time repeated calls, shuffling policy/question pairs each round.
    samples = {
        (policy_name, index): []
        for policy_name in routers
        for index in range(len(cases))
    }
    order = list(samples)
    generator = random.Random(seed)
    for _ in range(repeats):
        generator.shuffle(order)
        for policy_name, index in order:
            request = requests[index]
            start = time.perf_counter_ns()
            decision = routers[policy_name].route(request)
            after_route = time.perf_counter_ns()
            outcome = backend.respond(request, decision.model)
            after_dispatch = time.perf_counter_ns()

            # Dispatch spans route + backend lookup; both are local wall time.
            # Constructing/storing this sample happens after the timers stop.
            sample = TimingSample(
                router_ms=(after_route - start) / 1e6,
                local_dispatch_ms=(after_dispatch - start) / 1e6,
                decision=decision,
                outcome=outcome,
            )
            samples[policy_name, index].append(sample)

    # 5. Keep quality ONCE per unique question, even with many timing repeats.
    rows = []
    for policy_name in routers:
        for index, case in enumerate(cases):
            question_samples = samples[policy_name, index]
            decision = question_samples[0].decision
            outcome = question_samples[0].outcome
            for sample in question_samples:
                if sample.decision != decision or sample.outcome != outcome:
                    raise ValueError("nondeterministic outcome")

            router_ms = statistics.mean(
                sample.router_ms for sample in question_samples
            )
            dispatch_ms = statistics.mean(
                sample.local_dispatch_ms for sample in question_samples
            )
            rows.append({
                "policy": policy_name,
                "id": case["id"],
                "prompt": case["prompt"],
                "model": decision.model,
                "reason": decision.reason,
                "score": decision.score,
                "quality": outcome.quality,
                "cost_units": outcome.cost_units,
                "service_ms": outcome.service_ms,
                "router_ms": router_ms,
                "local_dispatch_ms": dispatch_ms,
                "modeled_e2e_ms": outcome.service_ms + dispatch_ms,
                "input_tokens_est": outcome.input_tokens_est,
                "output_tokens_est": outcome.output_tokens_est,
                "evidence": outcome.evidence,
            })

    # 6. Compare each policy with always-large on the SAME question sequence.
    baseline = [
        row["quality"] for row in rows if row["policy"] == "always_large"
    ]
    summary = []
    for policy_name in routers:
        policy_rows = [row for row in rows if row["policy"] == policy_name]
        quality = [row["quality"] for row in policy_rows]
        router_times = [
            sample.router_ms
            for (name, _), question_samples in samples.items()
            if name == policy_name
            for sample in question_samples
        ]
        # Modeled percentiles use each question's mean local dispatch time
        # plus its assumed service time. No artificial sleep is measured.
        modeled_times = [row["modeled_e2e_ms"] for row in policy_rows]
        summary.append({
            "policy": policy_name,
            "n": len(policy_rows),
            "quality": statistics.mean(quality),
            "quality_delta_vs_large": statistics.mean(
                value - baseline_value
                for value, baseline_value in zip(quality, baseline)
            ),
            "delta_bootstrap95": paired_interval(quality, baseline, seed),
            "mean_cost_units": statistics.mean(
                row["cost_units"] for row in policy_rows
            ),
            "large_fraction": statistics.mean(
                row["model"] == "large" for row in policy_rows
            ),
            "router_p50_ms": percentile(router_times, 0.5),
            "router_p95_ms": percentile(router_times, 0.95),
            "modeled_p50_ms": percentile(modeled_times, 0.5),
            "modeled_p95_ms": percentile(modeled_times, 0.95),
        })

    # 7. Include the evidence boundary, environment and exact input hashes.
    data_hashes = {
        name: hashlib.sha256(DATA.joinpath(name).read_bytes()).hexdigest()
        for name in [
            "synthetic_cases.json",
            "recorded_responses.json",
            "recorded_source_rows.json",
        ]
        if DATA.joinpath(name).is_file()
    }
    quality_metric = (
        "synthetic pass rate"
        if mode == "synthetic"
        else "mean human pairwise preference credit"
    )
    return {
        "mode": mode,
        "split": split if mode == "synthetic" else "recorded_convenience_sample",
        "seed": seed,
        "repeats": repeats,
        "threshold": threshold,
        "setup_ms": setup_ms,
        "evidence": backend.evidence,
        "quality_metric": quality_metric,
        "timing_note": (
            "Local router and dispatch wall time measured. Service time added "
            "analytically. No sleeping, network, or model inference. Setup, warmup, "
            "scoring, file I/O and bootstrap excluded from request timing."
        ),
        "cost_note": (
            "Hypothetical cost units. Approximate tokens ceil(chars/4). "
            "Small: (input+2*output)/1000. Large: six times small rates. "
            "No USD or historical billing claim."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "data_sha256": data_hashes,
        "summary": summary,
        "rows": rows,
    }


def write_report(report, outdir):
    """Save JSON, per-question CSV, summary CSV and a readable console table."""
    path = Path(outdir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "benchmark.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for filename, rows in [
        ("requests.csv", report["rows"]),
        ("summary.csv", report["summary"]),
    ]:
        with (path / filename).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    lines = [
        f"{report['mode'].upper()} - {report['quality_metric']}",
        report["evidence"],
        "policy          quality    cost units   router p95 ms   modeled p95 ms",
    ]
    for row in report["summary"]:
        lines.append(
            f"{row['policy']:<15} {row['quality']:7.3f}    "
            f"{row['mean_cost_units']:8.4f}    {row['router_p95_ms']:12.4f}   "
            f"{row['modeled_p95_ms']:12.1f}"
        )
    lines += [report["timing_note"], report["cost_note"]]
    text = "\n".join(lines)
    (path / "console.txt").write_text(text + "\n", encoding="utf-8")
    return text
