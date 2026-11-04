"""Determinism, exact historical replay, integrity and one-call integration."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from routing_workshop.backends import (
    DATA,
    RecordedBackend,
    SyntheticBackend,
    read_data,
    stable,
    verify_recordings,
)
from routing_workshop.integration import route_and_call
from routing_workshop.routers import Request, RuleRouter


class BackendTests(unittest.TestCase):
    def test_integration_calls_selected_backend_once(self):
        calls = []

        def small_backend(prompt):
            calls.append(prompt)
            return "hi"

        decision, answer = route_and_call(
            "Hello", RuleRouter(), {"small": small_backend}
        )
        self.assertEqual(calls, ["Hello"])
        self.assertEqual(answer, "hi")
        self.assertEqual(decision.model, "small")

        with self.assertRaises(ValueError):
            route_and_call("Hello", RuleRouter(), {})
        with self.assertRaises(TypeError):
            route_and_call("Hello", RuleRouter(), {"small": lambda prompt: 7})

    def test_stable_synthetic_pairing(self):
        cases = read_data("synthetic_cases.json")
        backend = SyntheticBackend(cases, seed=7)
        request = Request(cases[0]["prompt"])
        first = backend.respond(request, "small")

        backend.respond(Request(cases[1]["prompt"]), "large")
        self.assertEqual(first, backend.respond(request, "small"))
        self.assertNotEqual(stable(7, "a"), stable(8, "a"))
        self.assertIn("SYNTHETIC", first.evidence)

    def test_synthetic_rejects_missing_or_duplicates(self):
        case = read_data("synthetic_cases.json")[0]
        with self.assertRaises(ValueError):
            SyntheticBackend([case, case])
        with self.assertRaises(KeyError):
            SyntheticBackend([case]).respond(Request("unknown"), "small")

    @unittest.skipUnless(DATA.joinpath("recorded_responses.json").is_file(), "optional replay fixtures absent")
    def test_public_recordings_verified(self):
        result = verify_recordings()
        self.assertEqual(result["verified_questions"], 24)
        self.assertEqual(result["source_judgment_rows"], 50)

    @unittest.skipUnless(DATA.joinpath("recorded_responses.json").is_file(), "optional replay fixtures absent")
    def test_replay_exactness_and_pairwise_credit(self):
        backend = RecordedBackend()
        record = read_data("recorded_responses.json")[0]
        request = Request(record["prompt"])
        small = backend.respond(request, "small")
        large = backend.respond(request, "large")

        self.assertEqual(small.response, record["responses"]["gpt-3.5-turbo"])
        self.assertEqual(large.response, record["responses"]["gpt-4"])
        self.assertAlmostEqual(small.quality + large.quality, 1)
        self.assertIn("hypothetical", small.evidence)

    @unittest.skipUnless(DATA.joinpath("recorded_responses.json").is_file(), "optional replay fixtures absent")
    def test_replay_has_no_fallback(self):
        with self.assertRaises(KeyError):
            RecordedBackend().respond(Request("new question"), "small")

    @unittest.skipUnless(DATA.joinpath("recorded_responses.json").is_file(), "optional replay fixtures absent")
    def test_hash_tamper_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in [
                "recorded_manifest.json",
                "recorded_responses.json",
                "recorded_source_rows.json",
            ]:
                (root / name).write_bytes(DATA.joinpath(name).read_bytes())

            (root / "recorded_responses.json").write_text("[]")
            with self.assertRaisesRegex(ValueError, "hash"):
                verify_recordings(root)

    @unittest.skipUnless(DATA.joinpath("recorded_responses.json").is_file(), "optional replay fixtures absent")
    def test_rehashed_semantic_tamper_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in [
                "recorded_manifest.json",
                "recorded_responses.json",
                "recorded_source_rows.json",
            ]:
                (root / name).write_bytes(DATA.joinpath(name).read_bytes())

            # Rehashing a changed file must not bypass source-row comparisons.
            response_path = root / "recorded_responses.json"
            records = json.loads(response_path.read_text())
            records[0]["votes"] = ["tie"]
            response_path.write_text(json.dumps(records))

            manifest_path = root / "recorded_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["files"][response_path.name] = hashlib.sha256(
                response_path.read_bytes()
            ).hexdigest()
            manifest_path.write_text(json.dumps(manifest))

            with self.assertRaisesRegex(ValueError, "differs"):
                verify_recordings(root)
