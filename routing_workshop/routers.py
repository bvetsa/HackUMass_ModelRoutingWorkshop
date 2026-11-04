"""Choose a role from prompt text, before asking for an answer.

Read Request, Decision and RuleRouter first. LocalRouter is the next lesson;
FixedRouter and RandomRouter are comparison baselines. A router never sees
the evaluator's success labels, recorded answers or human preference votes.
"""

from collections import Counter
from dataclasses import dataclass
import hashlib
import math
import re


@dataclass(frozen=True, slots=True)
class Request:
    """The router's input: one prompt, with no hidden answer information.

    A dataclass creates the constructor for us: Request(prompt="Hello").
    frozen=True prevents changing the prompt after construction.
    """

    prompt: str

    def __post_init__(self):
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("prompt must be non-empty text")


@dataclass(frozen=True, slots=True)
class Decision:
    """The router's output: a role and reason, not an answer.

    For LocalRouter, score describes the large-class posterior. It is not
    confidence that a response will be correct.
    """

    model: str
    reason: str
    score: float | None = None

    def __post_init__(self):
        if self.model not in ("small", "large"):
            raise ValueError("unknown model role")


class RuleRouter:
    """Three branches: complexity keyword, long prompt, otherwise small.

    self means this particular router object. It stores the length limit so
    route() can use the same limit on every request.
    """

    def __init__(self, max_chars=180):
        if max_chars < 1:
            raise ValueError("max_chars must be positive")
        self.max_chars = max_chars

    def route(self, request):
        text = request.prompt.lower()

        # \b matches a word boundary: "prove" matches, "improved" does not.
        # Quotation and negation can fool this deliberately crude rule.
        complexity_keywords = (
            r"\b(prove|debug|derive|analy[sz]e|security|concurren\w*|"
            r"counterexample|trade-offs)\b"
        )
        if re.search(complexity_keywords, text):
            return Decision("large", "complexity keyword")

        if len(text) > self.max_chars:
            return Decision("large", "length threshold")

        return Decision("small", "short prompt without trigger")


def tokens(text):
    """Turn text into lowercase word/number pieces without another library."""
    return re.findall(r"[a-z]+|\d+", text.lower())


class LocalRouter:
    """Learn word counts using multinomial naive Bayes and add-one smoothing.

    training contains (prompt, needs_large) pairs. False is the authored small
    class; True is the authored large class. Development/test examples do not
    belong in training.
    """

    def __init__(self, training, threshold=0.6, margin=0.05):
        if not 0 <= threshold <= 1 or not 0 <= margin <= 0.5:
            raise ValueError("threshold in [0,1], margin in [0,.5] required")

        self.threshold = threshold
        self.margin = margin

        # Index 0 is the small class; index 1 is the large class.
        self.word_counts = [Counter(), Counter()]
        self.example_counts = [0, 0]
        self.vocabulary = set()

        for prompt, needs_large in training:
            class_index = int(bool(needs_large))
            words = tokens(prompt)
            self.word_counts[class_index].update(words)
            self.example_counts[class_index] += 1
            self.vocabulary.update(words)

        if not all(self.example_counts):
            raise ValueError("training requires both classes")

        self.word_totals = [sum(counts.values()) for counts in self.word_counts]

    def score(self, prompt):
        """Return a large-class posterior, or None when no words are known.

        Logarithms let us add word evidence instead of multiplying many tiny
        probabilities. See docs/WALKTHROUGH.md for the step-by-step explanation.
        """
        known_words = [word for word in tokens(prompt) if word in self.vocabulary]
        if not known_words:
            return None

        log_scores = []
        for class_index in (0, 1):
            # Prior: how often did this class appear in training?
            prior = self.example_counts[class_index] / sum(self.example_counts)
            log_prior = math.log(prior)

            # Add-one smoothing gives every class/word pair nonzero probability.
            denominator = self.word_totals[class_index] + len(self.vocabulary)
            log_word_probabilities = [
                math.log((self.word_counts[class_index][word] + 1) / denominator)
                for word in known_words
            ]
            log_scores.append(log_prior + sum(log_word_probabilities))

        # Convert the two log scores to one number between 0 and 1.
        # Clamping avoids exp() overflow; it does not calibrate the score.
        difference = max(-700, min(700, log_scores[0] - log_scores[1]))
        return 1 / (1 + math.exp(difference))

    def route(self, request):
        large_score = self.score(request.prompt)

        if large_score is None:
            return Decision("large", "no known words: fallback")

        # A score near the threshold selects large too. That is a costlier
        # default, not a guarantee of safety or answer quality.
        if abs(large_score - self.threshold) <= self.margin:
            return Decision("large", "ambiguous score: fallback", large_score)

        if large_score >= self.threshold:
            model = "large"
        else:
            model = "small"
        return Decision(model, "local text classifier", large_score)


class FixedRouter:
    """Always choose one role: the simplest comparison baseline."""

    def __init__(self, model):
        self.model = Decision(model, "fixed baseline").model

    def route(self, request):
        return Decision(self.model, "fixed baseline")


class RandomRouter:
    """A repeatable 50/50 baseline, stable for a given prompt and seed."""

    def __init__(self, seed=7):
        self.seed = seed

    def route(self, request):
        # Hashing turns the prompt/seed into repeatable bytes. The lowest bit
        # picks a role independently of call order and evaluator outcomes.
        prompt_bytes = f"{self.seed}:{request.prompt}".encode()
        digest = hashlib.sha256(prompt_bytes).digest()
        bit = digest[0] & 1
        model = "large" if bit else "small"
        return Decision(model, "seeded 50/50 baseline")
