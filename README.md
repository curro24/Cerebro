# Cerebro V2 — Ollama + Python + herramientas Windows

Esta versión añade acceso CONTROLADO al sistema:

- Router: decide especialista y herramientas.
- Coding: analiza/programa.
- General: responde preguntas generales.
- Filesystem: listar, leer y escribir archivos dentro de carpetas permitidas.
- Terminal: ejecutar comandos, con confirmación para comandos no seguros.
- Python: ejecutar scripts Python dentro de una carpeta de trabajo.
- Auditoría: registra acciones en `logs/audit.jsonl`.

## Seguridad

Por defecto solo se permite acceder a:

`workspace/`

Crea tus proyectos o copia un proyecto de prueba dentro de esa carpeta.

La terminal bloquea comandos peligrosos y pide confirmación para comandos fuera de una lista segura.

IMPORTANTE: esto NO es un sandbox de seguridad perfecto. No ejecutes la aplicación con privilegios de administrador y no le des acceso a carpetas sensibles.

## Requisitos

- Windows 10/11
- Python 3.10+
- Ollama ejecutándose
- Modelos:
  - `qwen3:1.7b`
  - `qwen3:4b`

Instalación:

```powershell
ollama pull qwen3:1.7b
ollama pull qwen3:4b
python main.py
```

## Comandos

Dentro de Cerebro:

`/help`      ayuda
`/tools`     herramientas disponibles
`/models`    modelos
`/exit`      salir

## Ejemplos

```text
Lista los archivos del proyecto.

Lee main.py y dime qué hace.

Busca errores en todo el proyecto.

Crea un archivo llamado hola.py que imprima Hola Mundo.

Ejecuta hola.py.
```

Para una operación de escritura o ejecución, Cerebro puede pedirte confirmación.

## Arquitectura

```text
                     USUARIO
                        |
                        v
                 +-------------+
                 |    ROUTER   |
                 +------+------+ 
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       CODING        GENERAL        TOOLS
          |             |             |
          |             |       +-----+-----+
          |             |       |     |     |
          |             |       v     v     v
          |             |    FILES  TERMINAL PYTHON
          |             |       \     |     /
          +-------------+--------\----+----/
                                  |
                                  v
                              workspace/
                                  |
                                  v
                               Windows
```

## V3 recomendada

- memoria persistente;
- critic/verificador;
- planificación multi-paso;
- herramientas de búsqueda;
- visión;
- permisos configurables;
- ejecución automática de tests;
- selección dinámica entre modelos pequeños y grandes.
