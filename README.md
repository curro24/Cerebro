# Cerebro V1 — Ollama + Python

V1 de una arquitectura de IA con 3 cerebros:

1. `router`: analiza la petición y decide qué especialista usar.
2. `coding`: especialista en programación.
3. `general`: especialista para el resto.

La V1 usa la API local de Ollama directamente por HTTP, sin dependencias Python externas.
El router devuelve una decisión estructurada en JSON.

## Requisitos

- Windows 10/11
- Python 3.10+
- Ollama instalado y ejecutándose
- Recomendado para tu RTX 4050 de 6 GB:
  - `qwen3:1.7b` para router
  - `qwen3:4b` para coding
  - `qwen3:4b` para general

Puedes cambiar los modelos en `config.json`.

## Instalación

Abre CMD/PowerShell dentro de esta carpeta:

```powershell
ollama pull qwen3:1.7b
ollama pull qwen3:4b
python main.py
```

Si `qwen3:1.7b` no aparece en tu instalación, cambia `router_model` por un modelo pequeño que tengas disponible.

## Uso

```text
Tú > escribe una pregunta
```

Ejemplos:

```text
Tú > Explícame qué es una lista enlazada en Python
Tú > Tengo este error: IndexError: list index out of range
Tú > ¿Qué diferencia hay entre TCP y UDP?
```

Para salir:

```text
/exit
```

Para ver modelos configurados:

```text
/models
```

## Arquitectura

```text
                         USUARIO
                            |
                            v
                     +--------------+
                     |    ROUTER    |
                     |  qwen3:1.7b  |
                     +------+-------+
                            |
                 +----------+----------+
                 |                     |
             coding                  general
            qwen3:4b                 qwen3:4b
                 |                     |
                 +----------+----------+
                            |
                            v
                         RESPUESTA
```

La idea importante es que el router NO resuelve el problema. Solo decide qué cerebro debe hacerlo.

## Próximas versiones

V2: memoria persistente.
V3: herramientas (Python, terminal, archivos).
V4: crítico/verificador.
V5: varios especialistas y ejecución de planes.
