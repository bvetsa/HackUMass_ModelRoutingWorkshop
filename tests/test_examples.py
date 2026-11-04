"""The documented beginner entry points must work from a participant checkout."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def run_example(self, *arguments):
        result = subprocess.run(
            [sys.executable, "-B", *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_first_lesson_runs(self):
        output = self.run_example("start.py")
        self.assertIn("Selected role: small", output)
        self.assertIn("Reason: short prompt without trigger", output)
        self.assertIn("It does not generate an answer.", output)

    def test_classifier_lesson_exposes_unknown_word_fallback(self):
        output = self.run_example("-m", "scripts.compare_routers")
        self.assertIn("DECISIONS ONLY", output)
        self.assertIn("no known words: fallback", output)

    def test_integration_lesson_labels_offline_output(self):
        output = self.run_example("-m", "scripts.integration_example")
        self.assertTrue("OFFLINE SYNTHETIC OUTCOME" in output or "OFFLINE RECORDED RESPONSE ONLY" in output)
