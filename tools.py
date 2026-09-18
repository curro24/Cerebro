from pathlib import Path
import subprocess
import json
import datetime
import os
import sys


class ToolError(RuntimeError):
    pass


class Tools:
    def __init__(self, workspace: Path, audit_file: Path):
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_file = audit_file.resolve()

    def _safe_path(self, relative: str) -> Path:
        if not relative:
            raise ToolError("Falta la ruta.")
        candidate = (self.workspace / relative).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError:
            raise ToolError("Ruta bloqueada: solo se permite acceder a workspace/.")
        return candidate

    def _audit(self, action, details):
        record = {
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "details": details
        }
        with self.audit_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def list_files(self, path="."):
        p = self._safe_path(path)
        if not p.exists():
            raise ToolError(f"No existe: {path}")
        if not p.is_dir():
            raise ToolError("La ruta no es una carpeta.")

        items = []
        for x in sorted(p.iterdir(), key=lambda z: (not z.is_dir(), z.name.lower())):
            items.append({
                "name": x.name,
                "type": "directory" if x.is_dir() else "file",
                "size": x.stat().st_size if x.is_file() else None
            })
        self._audit("list_files", {"path": path})
        return items

    def read_file(self, path):
        p = self._safe_path(path)
        if not p.exists() or not p.is_file():
            raise ToolError(f"No existe el archivo: {path}")
        if p.stat().st_size > 2_000_000:
            raise ToolError("Archivo demasiado grande para esta V2.")
        content = p.read_text(encoding="utf-8", errors="replace")
        self._audit("read_file", {"path": path, "bytes": len(content.encode("utf-8"))})
        return content

    def write_file(self, path, content, confirm=True):
        p = self._safe_path(path)
        if confirm:
            answer = input(f"\n[CONFIRMACIÓN] Escribir/modificar '{path}'? [s/N]: ").strip().lower()
            if answer not in {"s", "si", "sí", "y", "yes"}:
                return "Operación cancelada por el usuario."

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self._audit("write_file", {"path": path, "bytes": len(content.encode("utf-8"))})
        return f"Archivo escrito: {path}"

    def run_python(self, path, confirm=True):
        p = self._safe_path(path)
        if not p.exists() or p.suffix.lower() != ".py":
            raise ToolError("run_python requiere un archivo .py existente.")

        if confirm:
            answer = input(f"\n[CONFIRMACIÓN] Ejecutar Python '{path}'? [s/N]: ").strip().lower()
            if answer not in {"s", "si", "sí", "y", "yes"}:
                return "Ejecución cancelada por el usuario."

        proc = subprocess.run(
            [sys.executable, str(p)],
            cwd=str(self.workspace),
            capture_output=True,
            text=True,
            timeout=60
        )
        result = (
            f"RETURN CODE: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
        self._audit("run_python", {"path": path, "return_code": proc.returncode})
        return result[:20000]

    def terminal(self, command, confirm=True):
        command_lower = command.lower().strip()

        dangerous = [
            "format ", "diskpart", "shutdown", "restart-computer",
            "remove-item", "del ", "erase ", "rmdir ",
            "rd ", "reg delete", "bcdedit", "cipher /w"
        ]

        blocked = [
            "powershell -encodedcommand",
            "invoke-webrequest http",
            "curl http",
            "wget http"
        ]

        if any(x in command_lower for x in blocked):
            raise ToolError("Comando bloqueado por seguridad.")

        needs_confirmation = confirm or any(x in command_lower for x in dangerous)

        if needs_confirmation:
            answer = input(f"\n[CONFIRMACIÓN] Ejecutar comando:\n{command}\n[s/N]: ").strip().lower()
            if answer not in {"s", "si", "sí", "y", "yes"}:
                return "Comando cancelado por el usuario."

        proc = subprocess.run(
            command,
            cwd=str(self.workspace),
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        result = (
            f"RETURN CODE: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
        self._audit("terminal", {"command": command, "return_code": proc.returncode})
        return result[:20000]
