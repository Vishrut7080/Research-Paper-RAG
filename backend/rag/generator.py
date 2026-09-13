import os

from dotenv import load_dotenv
from groq import Groq

from backend.config import MAX_TOKENS, SYSTEM_PROMPT

load_dotenv()

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        _client = Groq(api_key=api_key)
    return _client


def generate_answer(query: str, context: str) -> str:
    """Call Groq with the retrieved context and a strict 'answer only from context' prompt."""
    response = get_client().chat.completions.create(
        model=os.getenv("GROQ_MODEL", "grok-2-latest"),
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return response.choices[0].message.content