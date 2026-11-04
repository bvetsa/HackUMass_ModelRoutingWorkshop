"""Connect a routing decision to exactly one supplied answer function.

A backend here means a function that accepts text and returns text.
No live model or provider API is implemented by this module.
"""

from collections.abc import Callable, Mapping

from .routers import Decision, Request


def route_and_call(
    prompt: str,
    router,
    backends: Mapping[str, Callable[[str], str]],
) -> tuple[Decision, str]:
    """Choose a role, call its function once, and return both results."""
    request = Request(prompt)
    decision = router.route(request)

    if decision.model not in backends:
        raise ValueError(f"No implemented backend supplied for {decision.model}")

    selected_backend = backends[decision.model]
    answer = selected_backend(prompt)

    if not isinstance(answer, str):
        raise TypeError("backend must return text")

    return decision, answer
