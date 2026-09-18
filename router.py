import json
from prompts import ROUTER_SYSTEM, ROUTER_SCHEMA


class Router:
    def __init__(self, ollama, model: str, temperature: float = 0.0):
        self.ollama = ollama
        self.model = model
        self.temperature = temperature

    def decide(self, user_text: str) -> dict:
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Decide el especialista para esta petición:\n\n"
                    + user_text
                ),
            },
        ]

        raw = self.ollama.chat(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            fmt=ROUTER_SCHEMA,
        )

        try:
            decision = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"El router no devolvió JSON válido: {raw}"
            ) from e

        specialist = decision.get("specialist")
        if specialist not in {"coding", "general"}:
            raise RuntimeError(f"Especialista inválido: {decision}")

        return decision
