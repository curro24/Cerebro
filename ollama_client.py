import json
import urllib.request
import urllib.error


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def chat(self, model, messages, temperature=0.2, fmt=None, tools=None, keep_alive="0"):
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive,
            "options": {"temperature": temperature}
        }
        if fmt is not None:
            payload["format"] = fmt
        if tools:
            payload["tools"] = tools

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + "/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=600) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise OllamaError(f"Ollama HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise OllamaError(
                "No se pudo conectar con Ollama. Comprueba que Ollama esté ejecutándose."
            ) from e

        try:
            result = json.loads(body)
            return result["message"]
        except (json.JSONDecodeError, KeyError) as e:
            raise OllamaError(f"Respuesta inesperada de Ollama: {body}") from e
