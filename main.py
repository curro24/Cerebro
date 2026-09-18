import json
from pathlib import Path

from ollama_client import OllamaClient, OllamaError
from router import Router
from agents import AgentManager


CONFIG_FILE = Path(__file__).with_name("config.json")


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_banner(config):
    print("=" * 64)
    print(" CEREBRO V1 — Ollama + Python")
    print(" Router + Coding + General")
    print("=" * 64)
    print(f"Router  : {config['router_model']}")
    print(f"Coding  : {config['coding_model']}")
    print(f"General : {config['general_model']}")
    print()
    print("Escribe /exit para salir o /models para ver la configuración.")
    print()


def main():
    config = load_config()

    ollama = OllamaClient(config["ollama_url"])

    router = Router(
        ollama=ollama,
        model=config["router_model"],
        temperature=config["temperature_router"],
    )

    agents = AgentManager(
        ollama=ollama,
        coding_model=config["coding_model"],
        general_model=config["general_model"],
        temperature=config["temperature_specialists"],
    )

    print_banner(config)

    while True:
        try:
            user_text = input("Tú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if not user_text:
            continue

        if user_text.lower() in {"/exit", "/quit", "/salir"}:
            print("Hasta luego.")
            break

        if user_text.lower() == "/models":
            print(f"Router : {config['router_model']}")
            print(f"Coding : {config['coding_model']}")
            print(f"General: {config['general_model']}")
            print()
            continue

        try:
            print("\n[Router] Analizando...")
            decision = router.decide(user_text)

            specialist = decision["specialist"]
            reason = decision["reason"]

            print(f"[Router] -> {specialist}")
            print(f"[Router] Motivo: {reason}")
            print(f"[{specialist}] Generando respuesta...\n")

            answer = agents.answer(specialist, user_text)

            print(answer)
            print()

        except OllamaError as e:
            print(f"\n[ERROR Ollama] {e}\n")
        except Exception as e:
            print(f"\n[ERROR] {e}\n")


if __name__ == "__main__":
    main()
