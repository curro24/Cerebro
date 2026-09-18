import json
from prompts import ROUTER_SYSTEM, ROUTER_SCHEMA


class Router:
    def __init__(self, ollama, model, temperature=0.0):
        self.ollama = ollama
        self.model = model
        self.temperature = temperature

    def decide(self, user_text):
        msg = self.ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM},
                {"role": "user", "content": user_text}
            ],
            temperature=self.temperature,
            fmt=ROUTER_SCHEMA
        )
        raw = msg.get("content", "")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Router no devolvió JSON válido: {raw}") from e

        if data.get("specialist") not in {"coding", "general"}:
            raise RuntimeError(f"Especialista inválido: {data}")
        if not isinstance(data.get("actions"), list):
            raise RuntimeError("El router no devolvió actions como lista.")
        return data
