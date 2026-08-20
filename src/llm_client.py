"""
llm_client.py
-------------
Thin wrapper around the Groq API (free tier) so the rest of the app
does not need to know which LLM provider is being used.

See README.md for how to get a free API key.
"""

from dotenv import load_dotenv
from groq import Groq
import json
import os
import re

load_dotenv()

# Default free-tier model on Groq
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def get_client() -> Groq:
    """Create a Groq client using the GROQ_API_KEY environment variable."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
            "free API key from https://console.groq.com/keys"
        )
    return Groq(api_key=api_key)
