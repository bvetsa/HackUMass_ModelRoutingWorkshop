"""Offline routing workshop; no network or third-party runtime dependencies.

Re-export the common input/output types and routers for convenient imports:
from routing_workshop import Request, RuleRouter
"""

from .routers import Decision, LocalRouter, Request, RuleRouter

__version__ = "1.0.0"
__all__ = ["Request", "Decision", "RuleRouter", "LocalRouter"]
