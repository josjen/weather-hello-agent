"""
greetings_quotes.py

Very small helper library exposing **two** convenience functions:

    • greet(name)        → "Hello <name>"
    • random_quote()     → random inspirational quote (str)

The latter tries to fetch a quote from the free, no‑auth *Quotable* API. If the
HTTP request fails for any reason (offline, rate‑limit, etc.), it falls back to
selecting one from a built‑in list.

Example
-------
>>> from greetings_quotes import greet, random_quote
>>> greet("Alice")
'Hello Alice'
>>> random_quote()
'You miss 100% of the shots you don’t take.'
"""
from __future__ import annotations
import random
import requests
from typing import List
import requests
from registry import mcp

__all__ = ["greet", "random_quote"]

_QUOTE_API = "https://api.quotable.io/random"
_FALLBACK_QUOTES: List[str] = [
    "The only limit to our realization of tomorrow is our doubts of today. – F. D. Roosevelt",
    "You miss 100% of the shots you don’t take. – Wayne Gretzky",
    "Strive not to be a success, but rather to be of value. – Albert Einstein",
    "The harder I work, the luckier I get. – Gary Player",
    "Do what you can, with what you have, where you are. – Theodore Roosevelt",
]

@mcp.tool()
def greet(name: str) -> str:
    """Return a friendly greeting for *name*."""
    return f"Hello {name}"

@mcp.tool()
def random_quote() -> str:
    """Return a random inspirational quote.

    Attempts to retrieve a fresh quote from *Quotable*. Falls back to a random
    entry from an internal list on network errors.
    """
    try:
        response = requests.get(_QUOTE_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("content", random.choice(_FALLBACK_QUOTES))
    except Exception:
        return random.choice(_FALLBACK_QUOTES)
