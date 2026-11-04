# Integration guide

> **Public edition:** Historical replay is reference material. This checkout ships synthetic cases and the integration example uses synthetic outcomes. Skip recorded-mode and verify commands.

## Working offline boundary

Run `python3 -m scripts.integration_example` from the repository root (the folder containing start.py). It takes a bundled
prompt, chooses a model role with `RuleRouter`, invokes the selected callable
once, and returns the historical response text. A miss is an error.

```python
from routing_workshop import RuleRouter
from routing_workshop.integration import route_and_call

# A fully working, simple application example with local callables.
backends = {
    "small": lambda prompt: "Local small handler received: " + prompt,
    "large": lambda prompt: "Local large handler received: " + prompt,
}
decision, answer = route_and_call("Extract the email", RuleRouter(), backends)
```

These handlers return fixed local strings. They are not language models. The
call boundary validates the selected role exists and that the backend returns
text. It does not add retries or exception suppression. A backend error
propagates to the application. It returns a decision reason for logging.

## Replacing the backend in a real application

No provider-specific or local-inference adapter ships in this workshop. To add
one, implement both selected roles as callables with signature `(str) -> str`.
Use the provider's current official SDK/documentation and a model available to
your account. Keep credentials in environment/secrets storage. This is future
implementation work, not a working command in this bundle.

Before enabling real traffic, define a request object that carries required
capabilities (vision, tools, context length, output schema), trust/privacy policy,
deadline and budget. Filter out ineligible models before applying a cost/quality
router. A larger model is not automatically safer, more private, or eligible.

Implement a single overall deadline that bounds route, queue, model request,
validation and any retry. Record attempted and completed calls. On failure,
retry only retryable errors within the remaining budget, respect idempotency,
and make escalation explicit. A fallback can increase latency and cost and may
still fail. Return an honest failure or human handoff when no eligible path
meets the contract. Do not silently send private input to a different provider.

## What to measure

Keep an application-owned evaluation set out of training and threshold tuning.
Gather paired outputs for all eligible models, preserve exact prompts and
parameters, and score with a stated rubric. Separate capability failure,
timeout, wrong answer and judge preference. Test short difficult prompts,
long simple prompts, unknown vocabulary, adversarially quoted keywords and
the domains your app actually serves.

Measure the full application wall clock, including routing, serialization,
queueing, inference, validation and retries. Track p50/p95 and error rates,
first-token latency separately if streaming, and actual token usage and charges.
Amortize startup/training and cache costs explicitly. This workshop's modeled
service numbers cannot substitute for those measurements.

For request logs, store model role, router version, threshold, decision reason,
timing and budget without raw sensitive prompts by default. Version any labeled
data and keep provenance. Run in shadow mode before a controlled rollout. Monitor
distribution shift and per-task regressions. Roll back to a tested fixed policy
if the routing layer makes the application less reliable.

## Routing versus cascading

This package implements one pre-call routing decision. A cascade would call a
small model, evaluate its answer, and perhaps call a larger model. That needs a
separate answer validator and accounting for both calls on escalation. No
cascade, semantic answer verifier, live failover, or production SLO enforcement
is implemented here.
