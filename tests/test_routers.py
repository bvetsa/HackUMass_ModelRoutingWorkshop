"""Input boundaries, rule behavior and local learning.

assertEqual(actual, expected) fails when the two values differ.
"""

import dataclasses
import unittest

from routing_workshop.backends import read_data
from routing_workshop.routers import Decision, LocalRouter, RandomRouter, Request, RuleRouter


class RouterTests(unittest.TestCase):
    def test_request_has_no_oracle_fields(self):
        request = Request("hello")
        field_names = [field.name for field in dataclasses.fields(request)]
        self.assertEqual(field_names, ["prompt"])
        self.assertFalse(hasattr(request, "needs_large"))
        with self.assertRaises((AttributeError, TypeError)):
            request.truth = True

    def test_empty_rejected(self):
        for prompt in ["", "  ", None, 9]:
            with self.assertRaises(ValueError):
                Request(prompt)

    def test_bad_model_rejected(self):
        with self.assertRaises(ValueError):
            Decision("magic", "unsupported")

    def test_rule_keywords_length_and_boundary(self):
        router = RuleRouter(max_chars=30)
        self.assertEqual(router.route(Request("Prove the claim")).model, "large")
        self.assertEqual(router.route(Request("improved")).model, "small")
        self.assertEqual(router.route(Request("x" * 30)).model, "small")
        self.assertEqual(router.route(Request("x" * 31)).model, "large")

    def test_rule_known_failure_is_visible(self):
        prompt = "Translate the word prove into French."
        self.assertEqual(RuleRouter().route(Request(prompt)).model, "large")

    def test_random_stable(self):
        router = RandomRouter(seed=7)
        request = Request("hello")
        self.assertEqual(router.route(request), router.route(request))
        roles = {
            router.route(Request("prompt " + str(index))).model
            for index in range(50)
        }
        self.assertEqual(roles, {"small", "large"})

    def test_local_learns_and_falls_back(self):
        training = [("extract email", False), ("prove theorem", True)]
        router = LocalRouter(training, threshold=0.5, margin=0)
        self.assertEqual(router.route(Request("extract email")).model, "small")
        self.assertEqual(router.route(Request("prove theorem")).model, "large")
        self.assertIn("fallback", router.route(Request("xyzzy")).reason)

    def test_local_ambiguous_and_config(self):
        training = [("same", False), ("same", True)]
        router = LocalRouter(training, threshold=0.5)
        self.assertIn("fallback", router.route(Request("same")).reason)
        for settings in [{"threshold": 2}, {"margin": -0.1}]:
            with self.assertRaises(ValueError):
                LocalRouter([("a", False), ("b", True)], **settings)
        with self.assertRaises(ValueError):
            LocalRouter([("a", False)])

    def test_split_separation(self):
        cases = read_data("synthetic_cases.json")
        prompts = {
            split: {case["prompt"] for case in cases if case["split"] == split}
            for split in ["train", "dev", "test"]
        }
        self.assertEqual(
            [len(prompts[split]) for split in ["train", "dev", "test"]],
            [32, 12, 36],
        )
        self.assertFalse(prompts["train"] & prompts["dev"])
        self.assertFalse(prompts["train"] & prompts["test"])
        self.assertFalse(prompts["dev"] & prompts["test"])
