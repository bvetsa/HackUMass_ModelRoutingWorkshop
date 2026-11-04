"""Your first routing example. Run with: python3 start.py

Read this file from top to bottom. Then follow RuleRouter.route() in
routing_workshop/routers.py. Change the prompt below and run this file again.
"""

from routing_workshop.routers import Request, RuleRouter

# 1. A prompt is the text someone would send to a language model.
prompt = "Extract the email from Contact: ada@example.org."

# 2. Wrap that text in the input object the router expects.
request = Request(prompt=prompt)

# 3. Create a router. Its default length cutoff is 180 characters.
router = RuleRouter()

# 4. Ask it to choose a role. Trace this call into routers.py.
decision = router.route(request)

# 5. Inspect the decision. No answer function or language model has run.
print("Prompt:", request.prompt)
print("Selected role:", decision.model)
print("Reason:", decision.reason)
print("Routing chooses a role. It does not generate an answer.")
