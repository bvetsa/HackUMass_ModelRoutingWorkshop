"""Compare rules with a classifier trained on the bundled training examples.

Run: python3 -m scripts.compare_routers
This prints decisions only. It does not generate or score answers.
"""

from routing_workshop.backends import read_data
from routing_workshop.routers import LocalRouter, Request, RuleRouter


def main():
    # JSON stores lists/dictionaries as text. read_data() loads that file.
    cases = read_data("synthetic_cases.json")

    # Learn from TRAIN only. Do not pass development/test labels to the router.
    training = []
    for case in cases:
        if case["split"] == "train":
            training.append((case["prompt"], case["needs_large"]))

    rules = RuleRouter()
    local = LocalRouter(training, threshold=0.6)
    prompts = [
        "Extract the email from Contact: ada@example.org.",
        "Prove it.",
        "Translate the word prove into French.",
        "xyzzy plover",  # No training words: the classifier falls back to large.
    ]

    print("DECISIONS ONLY: no model inference or quality measurement")
    for prompt in prompts:
        request = Request(prompt)
        rule_decision = rules.route(request)
        local_decision = local.route(request)
        print("\nPrompt:", prompt)
        print("Rules:", rule_decision.model, "|", rule_decision.reason)
        print("Local:", local_decision.model, "|", local_decision.reason)
        print("Large-class score:", local_decision.score)


if __name__ == "__main__":
    main()
