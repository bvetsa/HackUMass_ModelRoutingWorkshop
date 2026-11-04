"""Connect a router to bundled historical response text, with named functions.

Run: python3 -m scripts.integration_example
Only exact bundled prompts work; an unfamiliar prompt raises an error.
"""

from routing_workshop import Request, RuleRouter
from routing_workshop.backends import DATA, RecordedBackend, SyntheticBackend, read_data
from routing_workshop.integration import route_and_call


def main():
    # Verify the recordings before making them available.
    recorded = DATA.joinpath("recorded_responses.json").is_file()
    if recorded:
        backend = RecordedBackend()
        records = read_data("recorded_responses.json")
    else:
        records = read_data("synthetic_cases.json")
        backend = SyntheticBackend(records)
    prompt = records[0]["prompt"]

    # These functions look up old responses. They do not call a model/provider.
    def small_backend(text):
        outcome = backend.respond(Request(text), "small")
        return outcome.response

    def large_backend(text):
        outcome = backend.respond(Request(text), "large")
        return outcome.response

    backends = {"small": small_backend, "large": large_backend}
    router = RuleRouter()
    decision, answer = route_and_call(prompt, router, backends)

    if recorded:
        print("OFFLINE RECORDED RESPONSE ONLY")
        print("Historical model:", backend.model_names[decision.model])
    else:
        print("OFFLINE SYNTHETIC OUTCOME")
        print("Selected role:", decision.model)
    print("Reason:", decision.reason)
    print(answer)


if __name__ == "__main__":
    main()
