from pathlib import Path
import json

from ollama_client import OllamaClient
from router import Router


def main():
    config = json.loads(
        Path(__file__).with_name("config.json").read_text(encoding="utf-8")
    )

    client = OllamaClient(config["ollama_url"])
    router = Router(client, config["router_model"], 0.0)

    tests = [
        "Tengo un error TypeError en Python y no sé cómo solucionarlo.",
        "Explícame qué es la fotosíntesis.",
        "Necesito una función en JavaScript que ordene un array.",
        "¿Qué diferencia hay entre masa y peso?",
    ]

    for text in tests:
        result = router.decide(text)
        print(f"\n{text}")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
