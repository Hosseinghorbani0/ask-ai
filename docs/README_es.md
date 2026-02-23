# askai-python 🚀

<p align="center">
  🌍 <b>Readme:</b>
  <a href="../README.md"><img src="https://flagcdn.com/20x15/us.png" alt="English"> English</a> · 
  <a href="README_fa.md"><img src="https://flagcdn.com/20x15/ir.png" alt="Persian"> فارسی</a> · 
  <a href="README_zh.md"><img src="https://flagcdn.com/20x15/cn.png" alt="Chinese"> 中文</a> · 
  <a href="README_tr.md"><img src="https://flagcdn.com/20x15/tr.png" alt="Turkish"> Türkçe</a> · 
  <a href="README_ar.md"><img src="https://flagcdn.com/20x15/sa.png" alt="Arabic"> العربية</a> · 
  <a href="README_ru.md"><img src="https://flagcdn.com/20x15/ru.png" alt="Russian"> Русский</a> · 
  <a href="README_es.md"><img src="https://flagcdn.com/20x15/es.png" alt="Spanish"> Español</a> · 
  <a href="README_ja.md"><img src="https://flagcdn.com/20x15/jp.png" alt="Japanese"> 日本語</a>
</p>


<p align="center">
  <img src="../assets/banner.svg" alt="ask-ai animated banner" width="100%">
</p>

<p align="center">
  <b>Un SDK minimalista de Python para cambiar entre proveedores de IA con solo una línea de código.</b><br/>
  Cero frameworks. Cero servidores. Cero complicaciones.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Inicio Rápido (En 5 Segundos)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Detecta automáticamente OPENAI_API_KEY desde las variables de entorno
OpenAI().ask("Explícame los agujeros negros como si tuviera 5 años").text

# Cambia de proveedor instantáneamente
Groq().ask("Explícame los agujeros negros como si tuviera 5 años").text
```

---

## 🧐 ¿Por qué ask-ai?

- **Una función**: Simplemente llama a `.ask()`.
- **Múltiples proveedores**: Soporte para OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter.
- **Configuración cero**: Las claves se extraen automáticamente de las variables de entorno.
- **SDK primero, no un framework**: No interfiere con tu arquitectura de código.

## 🚫 Lo que este proyecto NO es

> ❌ No es un framework enorme de IA.
> ❌ No es un gateway de API.
> ❌ No es un sistema de memoria de agentes.

Este proyecto hace una sola cosa a la perfección: **Simplificar las llamadas a la API de los LLMs.**

---

## 🛠️ Uso Avanzado

### 🧰 Utilidades para el Desarrollador (Auto-Parsing)

<p align="center">
  <img src="../assets/features.svg" alt="ask-ai features parsing banner" width="100%">
</p>
¡Deja de escribir Regex para limpiar las respuestas! `ask-ai` incluye flags internos:

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (Elimina etiquetas de código como ```json)
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (Extrae SOLO el bloque de código, ignorando el resto)
code = ai.ask("Write a python script", code=True).text

# 3. Strip Tags (Elimina bloques <think> y etiquetas HTML)
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (Retorna directamente un Diccionario de Python)
data_dict = ai.ask("Extract info", json=True).json
print(data_dict['name'])
```

### 🔄 Reintentos y Límite de Tiempo (Resiliency)

<p align="center">
  <img src="../assets/resiliency.svg" alt="ask-ai resiliency banner" width="100%">
</p>
Maneja las limitaciones de tasa (`429`) y la pérdida de redes de forma automática:

```python
# Reintentará hasta 3 veces por errores de red con un límite de 10 segundos
response = ai.ask("Escribe un script de python", retry=3, timeout=10)
```

### ⚙ Configuración del Sistema
Ajusta directamente el rol del sistema y la temperatura:

```python
ai.advanced(
    temperature=0.7,
    prompt="Eres un ingeniero senior de DevOps."
)

print(ai.ask("¿Cómo optimizo un Dockerfile?").text)
```

---

## 🔗 Enlaces Importantes

- **Repositorio de GitHub**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (¡No olvides de dejarnos una estrella! ⭐)
- **Paquete PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **Sitio web oficial**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
