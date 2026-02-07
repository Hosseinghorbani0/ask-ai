# easyai

<p align="center">
  🌍 <b>Readme:</b>
  <a href="README.md"><img src="https://flagcdn.com/20x15/us.png" alt="English"> English</a> · 
  <a href="README_fa.md"><img src="https://flagcdn.com/20x15/ir.png" alt="Persian"> فارسی</a> · 
  <a href="README_zh.md"><img src="https://flagcdn.com/20x15/cn.png" alt="Chinese"> 中文</a> · 
  <a href="README_tr.md"><img src="https://flagcdn.com/20x15/tr.png" alt="Turkish"> Türkçe</a> · 
  <a href="README_ar.md"><img src="https://flagcdn.com/20x15/sa.png" alt="Arabic"> العربية</a> · 
  <a href="README_ru.md"><img src="https://flagcdn.com/20x15/ru.png" alt="Russian"> Русский</a> · 
  <a href="README_es.md"><img src="https://flagcdn.com/20x15/es.png" alt="Spanish"> Español</a> · 
  <a href="README_ja.md"><img src="https://flagcdn.com/20x15/jp.png" alt="Japanese"> 日本語</a>
</p>

# 🚀 easyai

**IA Simplificada.**
Conéctate a OpenAI, Groq, Google, Anthropic y más con una sola línea de código.

> Deja de reescribir código de IA para cada proveedor. Usa una línea. Cambia de modelo en cualquier momento.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ ¿Por qué easyai?

- **Sin bloqueo de SDK**: No aprendas 5 bibliotecas diferentes. Aprende una.
- **API Unificada**: `ai.ask()` funciona para texto, imágenes y audio en todos los proveedores.
- **Listo para Producción**: Seguridad de tipos integrada, manejo de errores y gestión de entornos.
- **Cero Configuración**: Detecta automáticamente claves API de tu entorno.

---

## 🚀 El Ejemplo Dorado (The Golden Example)

Mira el poder de `easyai` en 3 líneas de código:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "Explica la computación cuántica en una frase."

# Cambia proveedores al instante
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 Instalación

```bash
pip install easyai
```

---

## 📖 Guía de Inicio Rápido

### 1. Configuración
Exporta tus claves API (o pásalas explícitamente).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Uso Estándar
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("¡Hola Mundo!"))
```

### 3. Uso Avanzado (Profesional)
Controla `temperature`, `top_p` y personas del sistema (`prompt`) para resultados profesionales.

```python
ai.advanced(
    temperature=0.7,
    prompt="Eres un ingeniero DevOps senior."
)

print(ai.ask("¿Cómo optimizo un Dockerfile?"))
```

---

## 🔌 Proveedores Soportados

| Proveedor | Clase | Conjunto de Características |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | Todos los Modelos (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | Todos los Modelos (Claude 3.5, Opus) |
| **Google** | `Google` | Todos los Modelos (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | Todos los Modelos (Llama 3, Mixtral) |
| **Azure** | `Azure` | Todos los Modelos (Enterprise) |
| **OpenRouter**| `OpenRouter`| Todos los Modelos (100+) |

---

## ⭐ Apoya el Proyecto

Si este proyecto te ahorró tiempo, ¡por favor considera darle una estrella en GitHub! Nos ayuda a crecer.

**[¡Dale una Estrella!](https://github.com/Hosseinghorbani0/easyai)**

---
*Construido por [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*
