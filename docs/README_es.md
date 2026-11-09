# ask-ai

[![Versión en PyPI](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Versiones de Python](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**Un SDK de Python pequeño y tipado para llamar a varios proveedores de LLM mediante una API coherente.**
Úsalo en scripts y aplicaciones Python sin adoptar un framework de orquestación más amplio.

`ask-ai` es una biblioteca cliente, no un servicio alojado ni una pasarela. Crea un cliente de proveedor, realiza llamadas síncronas o asíncronas y recibe un objeto `Response` común. Los SDK de los proveedores son opcionales: instala solo los que utilices.

## Idiomas de la documentación

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## Contenido

- [Funciones](#funciones)
- [Requisitos e instalación](#requisitos-e-instalación)
- [Proveedores](#proveedores)
- [Inicio rápido](#inicio-rápido)
- [API pública](#api-pública)
- [Opciones de solicitud](#opciones-de-solicitud)
- [Reintentos, alternativas y enrutamiento](#reintentos-alternativas-y-enrutamiento)
- [Salida estructurada](#salida-estructurada)
- [Streaming y uso asíncrono](#streaming-y-uso-asíncrono)
- [Generación multimedia y descargas seguras](#generación-multimedia-y-descargas-seguras)
- [Sesiones y ciclo de vida](#sesiones-y-ciclo-de-vida-del-cliente)
- [Capacidades y observabilidad](#capacidades-y-observabilidad)
- [Arquitectura](#arquitectura)
- [Interfaz de línea de comandos](#interfaz-de-línea-de-comandos)
- [Compatibilidad y solución de problemas](#compatibilidad-y-solución-de-problemas)
- [Contribuciones, soporte y licencia](#contribuciones-soporte-y-licencia)

## Funciones

- API coherente `ask`, `ask_async`, `ask_stream` y `ask_stream_async`.
- Alternativa entre proveedores y enrutamiento basado en políticas.
- Reintentos para fallos transitorios, con plazos por llamada y globales.
- Metadatos de respuesta tipados, uso de tokens normalizado y hooks opcionales de observabilidad.
- Respuestas JSON y estructuradas validadas para proveedores compatibles.
- Sesiones de conversación opcionales en memoria.
- Endpoints compatibles con OpenAI Chat Completions, incluidos servidores locales.
- Descargas multimedia seguras controladas mediante políticas.

La API pública de solicitudes envía texto actualmente; los metadatos de capacidad no implican que se admita entrada de imágenes para visión. No se ofrece ejecución de llamadas a herramientas ni almacenamiento persistente de conversaciones.

## Requisitos e instalación

- Python 3.10 o posterior.
- El paquete base no tiene dependencias. Los SDK de proveedores y las bibliotecas multimedia/de salida estructurada se instalan como extras opcionales.

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI, Azure OpenAI, OpenRouter y endpoints compatibles
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic y jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # descargas multimedia seguras
python -m pip install "askai-python[all]"
```

Configura las credenciales en el entorno o pasa `api_key=` al crear el proveedor. No incluyas secretos directamente en el código.

## Proveedores

| Proveedor | Importación | Extra | Variable de entorno | Modelo predeterminado |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | Se requiere el nombre del deployment |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| Compatible con OpenAI | `OpenAICompatibleProvider` | `openai` | Ninguna (opcional) | Obligatorio al crear |

Azure también requiere `AZURE_OPENAI_ENDPOINT`; indica el deployment como `model=` o mediante `AZURE_OPENAI_DEPLOYMENT_NAME`. `AZURE_OPENAI_API_VERSION` tiene como valor predeterminado `2024-06-01`. El proveedor compatible requiere `base_url` HTTP(S) absoluto y un modelo; `api_key` puede omitirse para endpoints locales.

`capabilities()` devuelve las capacidades declaradas para texto, streaming, streaming asíncrono, salida estructurada, llamadas a herramientas, generación de imágenes/audio y visión. No garantiza que un modelo o una cuenta concretos tengan habilitada cada función. La ejecución de herramientas y la entrada de visión no se exponen como funciones generales de solicitud.

## Inicio rápido

```python
from ask_ai import OpenAI

client = OpenAI()  # Lee OPENAI_API_KEY
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## API pública

| Método | Resultado | Descripción |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | Solicitud síncrona |
| `await provider.ask_async(query, **options)` | `Response` | Solicitud asíncrona nativa |
| `provider.ask_stream(query, **options)` | Iterador de cadenas | Streaming de texto síncrono |
| `async for chunk in provider.ask_stream_async(...)` | Iterador asíncrono | Streaming de texto asíncrono |
| `provider.ask_stream_events(...)` | Iterador de eventos | Streaming síncrono tipado |
| `provider.ask_stream_events_async(...)` | Iterador asíncrono de eventos | Streaming asíncrono tipado |

`Response` ofrece `text`, el texto original `raw`, `json` analizado, `parsed`/`pydantic` si se solicitó `response_model`, además de `media`, `usage` y `metadata` opcionales. `response.json` analiza el texto; utiliza `json=True` para pedir salida JSON o `response_model=...` si necesitas validación.

## Opciones de solicitud

Pasa opciones a cada solicitud o establece valores predeterminados con `provider.advanced(...)`. Las opciones de la solicitud prevalecen.

| Opción | Uso |
|---|---|
| `temperature`, `max_tokens`, `top_p` | Controles de generación comunes |
| `frequency_penalty`, `presence_penalty`, `stop` | Controles compatibles según el proveedor |
| `system_message` (`system`, `prompt`) | Instrucción del sistema |
| `timeout` | Límite por llamada (30 segundos predeterminados en clientes de proveedor) |
| `total_timeout` | Plazo para la operación completa, incluidos los reintentos |
| `retry` | Reintentos adicionales; predeterminado 2 (hasta 3 intentos) |
| `json=True` | Solicita formato JSON y permite analizar `response.json` |
| `response_model`, `validation_retries` | Analiza y valida un modelo estructurado compatible |
| `output_type` | Solicita generación compatible de `image` o `audio` |
| `clean`, `strip`, `code` | Limpia o extrae texto al acceder a `response.text` |
| `strict_options=True` | Falla ante opciones desconocidas en vez de avisar |

La compatibilidad depende del proveedor y del modelo. Las opciones desconocidas generan avisos por defecto; el modo estricto lanza `ValueError`. `safe_mode` está obsoleto y no tiene comportamiento definido. Los tipos de salida no compatibles producen un error explícito.

## Reintentos, alternativas y enrutamiento

Por defecto se realizan dos reintentos ante fallos transitorios reintentables (hasta tres intentos). Los errores de solicitud inválida y autenticación no se reintentan. Se respeta `Retry-After` con un límite de 30 segundos. `timeout` limita una llamada; `total_timeout` limita toda la operación.

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

La cadena de alternativas solo avanza ante errores reintentables. `Router` permite elegir según políticas y limita el total mediante `max_attempts`. Reintentar o recurrir a alternativas puede generar cargos adicionales; usa un plazo global y pocos reintentos para controlar coste y latencia. Un stream no se reintenta después de emitir fragmentos.

## Salida estructurada

Se admiten modelos Pydantic, dataclasses, `TypedDict` y esquemas JSON. La respuesta sigue siendo un objeto `Response`; accede al resultado validado con `.parsed`.

```python
from pydantic import BaseModel
from ask_ai import OpenAI

class Summary(BaseModel):
    title: str
    points: list[str]

response = OpenAI().ask(
    "Summarize the water cycle.",
    response_model=Summary,
    validation_retries=1,
)
print(response.parsed.title)
```

La validación se realiza localmente y el soporte de esquemas nativos varía. Una salida no válida genera un error de validación estructurada. No se admite validación estructurada en el streaming de sesiones.

## Streaming y uso asíncrono

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

Usa `ask_async()` y `ask_stream_async()` con `await` y `async for`. Los eventos tipados de streaming incluyen `TextDelta`, `UsageUpdate`, `Completed` y `Error`. `ToolCall` está exportado como tipo de evento, pero los adaptadores actuales no emiten eventos de llamadas a herramientas. Usa `ask_stream_events()` o `ask_stream_events_async()` para recibir los eventos. Gestiona cancelaciones y excepciones del proveedor en tu aplicación.

## Generación multimedia y descargas seguras

Algunos proveedores implementan generación de imágenes o audio mediante `output_type="image"` o `"audio"`; la disponibilidad depende del proveedor y del modelo. La API no acepta actualmente imágenes como entrada de visión.

Las descargas seguras requieren el extra `httpx`. Por defecto exigen HTTPS, rechazan redirecciones y direcciones DNS no públicas, limitan los datos a 25 MiB y el tiempo a 30 segundos. Se pueden restringir hosts y tipos MIME:

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

Usa `allow_private=True` solo con hosts privados de confianza. Una política de descarga no vuelve seguros los enlaces generados por proveedores para otros usos.

## Sesiones y ciclo de vida del cliente

`provider.session()` crea una conversación opcional en memoria:

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

El historial permanece en la memoria del proceso, no se persiste y `max_messages` lo limita por pares usuario/asistente. Las llamadas síncronas concurrentes se serializan entre sí, al igual que las asíncronas; no mezcles ambas modalidades concurrentemente en la misma sesión.

Los proveedores admiten `close()`/`aclose()` y gestores de contexto síncronos/asíncronos. Cierra los clientes al terminar. El cliente asíncrono en caché queda asociado al primer event loop que lo usa; crea un proveedor por loop.

## Capacidades y observabilidad

Consulta `provider.capabilities()` para las capacidades declaradas. Añade un hook de observabilidad con `provider.use(Observability(...))` para recibir proveedor, modelo, latencia, reintentos y uso normalizado de tokens. El coste estimado solo se calcula si se proporcionan precios y el proveedor informa del uso.

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

No envíes prompts sensibles ni credenciales a tus handlers de telemetría. Los errores de un hook no interrumpen la solicitud.

## Arquitectura

`ask_ai` reúne una clase base para proveedores, adaptadores SDK específicos, un `Response` común, `Router`, `ConversationSession` opcionales y utilidades de salida estructurada y seguridad multimedia. Los SDK se importan de forma opcional, por lo que no es necesario instalar todas las integraciones para importar el paquete. Las solicitudes no pasan por un servicio propio.

## Interfaz de línea de comandos

El comando `ask-ai` admite OpenAI, Groq, Google, OpenRouter, Azure y Anthropic:

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

El CLI utiliza las credenciales del proveedor. El proveedor genérico compatible con OpenAI solo está disponible en la API Python, no entre las opciones actuales del CLI.

## Compatibilidad y solución de problemas

- **Python:** 3.10–3.13 aparecen en los clasificadores; el mínimo declarado es 3.10.
- **Tipos:** el paquete incluye `ask_ai/py.typed`.
- **Falta un SDK:** instala el extra correspondiente, por ejemplo `askai-python[openai]`.
- **Faltan credenciales:** configura la variable indicada o pasa `api_key=`.
- **Error de Azure:** configura endpoint, clave y deployment/modelo.
- **Opción desconocida:** revisa la escritura o usa `strict_options=True`.
- **Error de event loop:** no reutilices un proveedor asíncrono en otro loop.
- **Salida estructurada inválida:** revisa el modelo/esquema; cada reintento puede generar otro cargo.
- **API real:** las pruebas simuladas no garantizan la compatibilidad con el proveedor en vivo; las pruebas reales opcionales pueden tener coste.

## Contribuciones, soporte y licencia

Envía errores y solicitudes mediante el [seguimiento de incidencias](https://github.com/Hosseinghorbani0/ask-ai/issues). Las contribuciones deben ser acotadas e incluir pruebas y documentación para cambios de comportamiento. Ejecuta `python -m pytest -q` y `ruff check .` antes de enviar una propuesta. Consulta [CHANGELOG.md](../CHANGELOG.md).

El proyecto utiliza la [licencia MIT](../LICENSE). Para preguntas e informes, incluye un ejemplo mínimo reproducible y elimina claves API, datos personales y demás secretos. Más información en [PyPI](https://pypi.org/project/askai-python/) y el [repositorio](https://github.com/Hosseinghorbani0/ask-ai).
