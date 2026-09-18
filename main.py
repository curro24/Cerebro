import json
from pathlib import Path

from ollama_client import OllamaClient, OllamaError
from router import Router
from tools import Tools, ToolError
from prompts import CODING_SYSTEM, GENERAL_SYSTEM


CONFIG = Path(__file__).with_name("config.json")


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def ask_model(client, model, system, user, temperature):
    msg = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temperature
    )
    return msg.get("content", "")


def tool_execute(tools, action, config):
    name = action.get("tool")
    if name == "list_files":
        return tools.list_files(action.get("path", "."))
    if name == "read_file":
        return tools.read_file(action.get("path", ""))
    if name == "write_file":
        return tools.write_file(
            action.get("path", ""),
            action.get("content", ""),
            config["ask_confirmation_for_writes"]
        )
    if name == "run_python":
        return tools.run_python(
            action.get("path", ""),
            config["ask_confirmation_for_terminal"]
        )
    if name == "terminal":
        return tools.terminal(
            action.get("command", ""),
            config["ask_confirmation_for_terminal"]
        )
    raise ToolError(f"Herramienta desconocida: {name}")


def main():
    config = load_config()

    workspace = Path(__file__).with_name(config["workspace"])
    audit = Path(__file__).with_name("logs") / "audit.jsonl"

    client = OllamaClient(config["ollama_url"])
    router = Router(client, config["router_model"], config["temperature_router"])
    tools = Tools(workspace, audit)

    print("=" * 68)
    print(" CEREBRO V2 — Router + Coding + General + Windows Tools")
    print("=" * 68)
    print(f"Workspace permitido: {workspace.resolve()}")
    print(f"Router:  {config['router_model']}")
    print(f"Coding:  {config['coding_model']}")
    print(f"General: {config['general_model']}")
    print("Escribe /help para ayuda, /exit para salir.\n")

    while True:
        try:
            user = input("Tú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            return

        if not user:
            continue
        if user.lower() in {"/exit", "/quit", "/salir"}:
            print("Hasta luego.")
            return
        if user.lower() == "/help":
            print("""
Ejemplos:
  Lista los archivos del proyecto.
  Lee main.py.
  Busca errores en el proyecto.
  Crea un archivo hola.py.
  Ejecuta hola.py.
  ¿Qué diferencia hay entre TCP y UDP?

Las operaciones de escritura y ejecución piden confirmación.
""")
            continue
        if user.lower() == "/tools":
            print("list_files, read_file, write_file, run_python, terminal")
            continue
        if user.lower() == "/models":
            print(json.dumps({
                "router": config["router_model"],
                "coding": config["coding_model"],
                "general": config["general_model"]
            }, indent=2))
            continue

        try:
            print("\n[ROUTER] Analizando...")
            decision = router.decide(user)
            specialist = decision["specialist"]
            print(f"[ROUTER] -> {specialist}")
            print(f"[ROUTER] {decision['reason']}")

            context_parts = []
            actions = decision.get("actions", [])

            for action in actions:
                print(f"[TOOL] {action.get('tool')}")
                result = tool_execute(tools, action, config)
                context_parts.append(
                    f"HERRAMIENTA: {action.get('tool')}\nRESULTADO:\n{result}"
                )

            context = "\n\n".join(context_parts)

            system = CODING_SYSTEM if specialist == "coding" else GENERAL_SYSTEM
            model = config["coding_model"] if specialist == "coding" else config["general_model"]

            prompt = user
            if context:
                prompt += (
                    "\n\nINFORMACIÓN OBTENIDA DE LAS HERRAMIENTAS. "
                    "Usa estos datos y no inventes otros:\n" + context
                )

            print(f"[{specialist.upper()}] Generando...\n")
            answer = ask_model(
                client,
                model,
                system,
                prompt,
                config["temperature_specialists"]
            )
            print(answer[:config["max_output_chars"]])
            print()

        except (OllamaError, ToolError, RuntimeError) as e:
            print(f"\n[ERROR] {e}\n")
        except Exception as e:
            print(f"\n[ERROR INESPERADO] {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()
