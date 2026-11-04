"""Supply evaluation outcomes after a router chooses a role.

SyntheticBackend returns designed PASS/FAIL placeholders.
RecordedBackend returns exact historical text from bundled files.
Neither class runs a language model, calls an API or measures inference time.
"""

from dataclasses import dataclass
from importlib.resources import files
import hashlib
import json
import math


# Resolve data relative to this Python package, never the presenter's folders.
DATA = files("routing_workshop").joinpath("data")


def read_data(name):
    """Read a bundled JSON file into Python lists/dictionaries."""
    resource = DATA.joinpath(name)
    if not resource.is_file():
        raise ValueError(f"Optional replay fixture {name} is absent. Use synthetic mode for the public workshop.")
    text = resource.read_text(encoding="utf-8")
    return json.loads(text)


def stable(seed, key):
    """Turn a seed/key into a repeatable number in [0, 1)."""
    digest = hashlib.sha256(f"{seed}:{key}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


@dataclass(frozen=True)
class Outcome:
    """An evaluator result, including explicitly assumed service metrics.

    quality belongs to evaluation. It is never passed to the router.
    """

    response: str
    quality: float
    service_ms: float
    cost_units: float
    input_tokens_est: int
    output_tokens_est: int
    evidence: str


def assumptions(prompt, response, model, jitter=0.5):
    """Calculate teaching assumptions, not actual tokens, billing or latency."""
    input_tokens = math.ceil(len(prompt) / 4)
    output_tokens = math.ceil(len(response) / 4)

    if model == "small":
        cost_factor = 1
        base_ms = 80
        ms_per_output_token = 1
    else:
        cost_factor = 6
        base_ms = 320
        ms_per_output_token = 2

    cost_units = cost_factor * (input_tokens + 2 * output_tokens) / 1000
    service_ms = base_ms + ms_per_output_token * output_tokens + 40 * jitter
    return service_ms, cost_units, input_tokens, output_tokens


class SyntheticBackend:
    """A designed teaching world, hidden from the prompt-only router."""

    evidence = "SYNTHETIC: designed hidden outcomes, no LLM inference"

    def __init__(self, cases, seed=7):
        self.seed = seed
        self._truth = {
            case["prompt"]: bool(case["needs_large"]) for case in cases
        }
        if len(self._truth) != len(cases):
            raise ValueError("duplicate prompts")

    def respond(self, request, model):
        if model not in ("small", "large"):
            raise ValueError("unknown role")

        needs_large = self._truth[request.prompt]
        if model == "small":
            pass_probability = 0.26 if needs_large else 0.92
        else:
            pass_probability = 0.87 if needs_large else 0.95

        # Each prompt/role/seed has one fixed draw. Policy order cannot change it.
        quality_key = "quality:" + request.prompt + ":" + model
        passed = stable(self.seed, quality_key) < pass_probability
        response = f"Synthetic {model} outcome: " + ("PASS" if passed else "FAIL")

        time_key = "time:" + request.prompt + ":" + model
        jitter = stable(self.seed, time_key)
        service_ms, cost_units, input_tokens, output_tokens = assumptions(
            request.prompt, response, model, jitter
        )
        return Outcome(
            response=response,
            quality=float(passed),
            service_ms=service_ms,
            cost_units=cost_units,
            input_tokens_est=input_tokens,
            output_tokens_est=output_tokens,
            evidence=self.evidence,
        )


def verify_recordings(data_dir=None):
    """Check file hashes AND transformations from selected source judgment rows.

    This establishes consistency with bundled dataset rows. It does not prove
    answer correctness, authenticate historical execution or endorse the votes.
    The optional data_dir supports integrity tests with temporary copies.
    """
    root = DATA if data_dir is None else data_dir

    def load(name):
        return json.loads(root.joinpath(name).read_text(encoding="utf-8"))

    # 1. Check that the selected data files still match their recorded hashes.
    manifest = load("recorded_manifest.json")
    for name, expected_hash in manifest["files"].items():
        actual_hash = hashlib.sha256(root.joinpath(name).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"fixture hash mismatch: {name}")

    source_rows = load("recorded_source_rows.json")
    records = load("recorded_responses.json")
    if len({record["id"] for record in records}) != len(records):
        raise ValueError("duplicate recording ids")

    question_ids = [int(record["id"].split("-")[1]) for record in records]
    if question_ids != manifest["question_ids"]:
        raise ValueError("recording selection mismatch")

    # 2. Reconstruct each response pair and vote list from its original rows.
    used_indices = []
    for record in records:
        question_id = int(record["id"].split("-")[1])
        matching_rows = [
            row for row in source_rows if row["question_id"] == question_id
        ]
        if not matching_rows:
            raise ValueError("missing source rows")

        votes = []
        responses = {}
        for row in matching_rows:
            if row["turn"] != 1:
                raise ValueError("only first turns supported")
            if {row["model_a"], row["model_b"]} != {"gpt-3.5-turbo", "gpt-4"}:
                raise ValueError("source model pair mismatch")

            for side in ("a", "b"):
                conversation = row["conversation_" + side]
                if (
                    conversation[0]["role"] != "user"
                    or conversation[1]["role"] != "assistant"
                    or conversation[0]["content"] != record["prompt"]
                ):
                    raise ValueError("source prompt mismatch")

                model_name = row["model_" + side]
                answer = conversation[1]["content"]
                if model_name in responses and responses[model_name] != answer:
                    raise ValueError("inconsistent response")
                responses[model_name] = answer

            winner = row["winner"]
            if winner not in ("model_a", "model_b", "tie", "tie (bothbad)"):
                raise ValueError("unknown preference label")
            if winner.startswith("tie"):
                votes.append("tie")
            else:
                votes.append(row[winner])

        indices = [row["source_row_index"] for row in matching_rows]
        used_indices.extend(indices)
        if (
            responses != record["responses"]
            or votes != record["votes"]
            or indices != record["source_row_indices"]
        ):
            raise ValueError("recording differs from source")

    # 3. Ensure no bundled source judgment row was silently dropped.
    source_indices = [row["source_row_index"] for row in source_rows]
    if sorted(used_indices) != sorted(source_indices):
        raise ValueError("unused source rows")

    return {
        "verified_questions": len(records),
        "source_judgment_rows": len(source_rows),
        "revision": manifest["revision"],
        "license": manifest["license"],
    }


class RecordedBackend:
    """Look up exact historical response text and human preference credit."""

    evidence = "RECORDED REPLAY: historical responses, hypothetical service cost/time"
    model_names = {"small": "gpt-3.5-turbo", "large": "gpt-4"}

    def __init__(self):
        verify_recordings()
        self._records = {
            record["prompt"]: record
            for record in read_data("recorded_responses.json")
        }

    def respond(self, request, model):
        if model not in self.model_names:
            raise ValueError("unknown role")
        if request.prompt not in self._records:
            raise KeyError(
                "Replay supports exact bundled prompts only. No synthetic fallback."
            )

        record = self._records[request.prompt]
        model_name = self.model_names[model]
        response = record["responses"][model_name]
        votes = record["votes"]

        # A vote for this model earns 1, against earns 0, and a tie earns 0.5.
        # This is preference credit, not proof that the answer is correct.
        vote_credits = [
            0.5 if vote == "tie" else float(vote == model_name) for vote in votes
        ]
        quality = sum(vote_credits) / len(votes)
        service_ms, cost_units, input_tokens, output_tokens = assumptions(
            request.prompt, response, model
        )
        return Outcome(
            response=response,
            quality=quality,
            service_ms=service_ms,
            cost_units=cost_units,
            input_tokens_est=input_tokens,
            output_tokens_est=output_tokens,
            evidence=self.evidence,
        )
