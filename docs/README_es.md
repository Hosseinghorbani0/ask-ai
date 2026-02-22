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
  <b>Un SDK de Python minimalista para cambiar entre proveedores de LLM en una sola línea.</b><br/>
  Sin frameworks. Sin servidores. Sin ingeniería excesiva.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Inicio Rápido (5 segundos)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Detecta automáticamente OPENAI_API_KEY desde el entorno
OpenAI().ask("Explica los agujeros negros como si tuviera 5 años").text

# Cambia de proveedor al instante
Groq().ask("Explica los agujeros negros como si tuviera 5 años").text
```

---

## 🧐 ¿Por qué ask-ai?

- **Una sola función**: Solo llama a `.ask()`
- **Múltiples proveedores**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **Sin configuración**: Las claves se extraen del entorno automáticamente.
- **SDK primero, no un framework**: No se interpone en tu camino.

## ⚖️ Cómo se compara

| Característica | ask-ai | LangChain |
| -------------- | ------ | --------- |
| Tiempo de conf. | 30 seg | 1 hora |
| Curva de aprend.| ⭐ | ⭐⭐⭐⭐⭐ |
| Soporte Async | ⏳ *(Pronto)* | ⚠️ Complejo |
| Reintentos | ✅ Integrado | ❌ Manual |
| Requiere Gateway | ❌ No | ❌ No |
| Líneas para cambiar| **1** | 20+ |

## 🚫 Lo que este proyecto NO es

> ❌ No es un framework de IA
> ❌ No es un API gateway
> ❌ No es un sistema de memoria para agentes

Hace una sola cosa perfectamente: **Simplificar la llamada a las API de los LLMs.**

---

## 🛠️ Uso Avanzado

### Resiliencia Integrada (Retries & Timeout)
Maneja los límites de tasa (`429`) y caídas de red automáticamente:

```python
from ask_ai import OpenAI
ai = OpenAI()

# Reintentará hasta 3 veces en errores de red, timeout por defecto de 10s
response = ai.ask("Escribe un script de python complejo", retry=3, timeout=10)
```

### Configuración del Sistema
Establece prompts del sistema y temperatura (temperature) directamente:

```python
ai.advanced(
    temperature=0.7,
    prompt="Eres un ingeniero de DevOps senior."
)

print(ai.ask("¿Cómo optimizo un Dockerfile?").text)
```

---

## 🔗 Enlaces Importantes

- **Repositorio en GitHub**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (¡Danos una estrella! ⭐)
- **PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **Sitio Web Oficial**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
