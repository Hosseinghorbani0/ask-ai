# ask-ai

<p align="center">
  🌍 <b>Readme:</b>
  <a href="README.md"><img src="https://flagcdn.com/20x15/us.png" alt="English"> English</a> · 
  <a href="docs/README_fa.md"><img src="https://flagcdn.com/20x15/ir.png" alt="Persian"> فارسی</a> · 
  <a href="docs/README_zh.md"><img src="https://flagcdn.com/20x15/cn.png" alt="Chinese"> 中文</a> · 
  <a href="docs/README_tr.md"><img src="https://flagcdn.com/20x15/tr.png" alt="Turkish"> Türkçe</a> · 
  <a href="docs/README_ar.md"><img src="https://flagcdn.com/20x15/sa.png" alt="Arabic"> العربية</a> · 
  <a href="docs/README_ru.md"><img src="https://flagcdn.com/20x15/ru.png" alt="Russian"> Русский</a> · 
  <a href="docs/README_es.md"><img src="https://flagcdn.com/20x15/es.png" alt="Spanish"> Español</a> · 
  <a href="docs/README_ja.md"><img src="https://flagcdn.com/20x15/jp.png" alt="Japanese"> 日本語</a>
</p>

<p align="center">
  <b>A minimal Python SDK to switch between LLM providers in one line.</b><br/>
  No frameworks. No servers. No overengineering.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Quick Start (5 seconds)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Auto-detects OPENAI_API_KEY from environment
OpenAI().ask("Explain black holes like I'm 5").text

# Switch provider effortlessly
Groq().ask("Explain black holes like I'm 5").text
```

---

## 🧐 Why ask-ai?

- **One function**: Just call `.ask()`
- **Multiple providers**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **Zero config**: Keys are pulled from the environment automatically
- **SDK-first, not a framework**: It stays out of your way.

## ⚖️ How it compares

| Feature        | ask-ai | LangChain |
| -------------- | ------ | --------- |
| Setup time     | 30 sec | 1 hour    |
| Learning curve | ⭐      | ⭐⭐⭐⭐⭐     |
| Async support  | ⏳ *(Coming soon)* | ⚠️ Complex |
| Retry/Timeout  | ✅ Built-in | ❌ Manual |
| Gateway needed | ❌ No      | ❌ No      |
| Lines to switch| **1**      | 20+       |

## 🚫 What this project is NOT

> ❌ Not an AI framework  
> ❌ Not an API gateway  
> ❌ Not an agent memory system  

It does one thing perfectly: **Simplifying the API call to LLMs.**

---

## 🛠️ Advanced Usage

### Built-in Retries & Timeout (Resiliency)
Handle rate limits (`429`) and network drops automatically:

```python
from ask_ai import OpenAI
ai = OpenAI()

# Will retry up to 3 times on RateLimit/Network errors, with generic timeout
response = ai.ask("Write a script", retry=3, timeout=10)
```

### System Configuration 
Set system prompts and temperature directly:

```python
ai.advanced(
    temperature=0.7,
    prompt="You are a senior DevOps engineer."
)

print(ai.ask("How do I optimize a Dockerfile?").text)
```

---

## 🗺️ Roadmap

- [x] OpenAI, Groq, Gemini, Anthropic, Azure, OpenRouter support
- [x] Text to Image (DALL-E) and Text to Audio
- [x] Automated Retry & Timeout controls
- [ ] Async Support (`await ask_async`)
- [ ] Provider Fallback (`ask(..., providers=[OpenAI, Groq])`)
- [ ] Streaming Support (`ask_stream`)
- [ ] Structured Output (Pydantic Support)

---

## 🔗 Important Links

- **PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **GitHub Repository**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (Star us! ⭐)
- **Official Website**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
- **Bug Tracker**: [Report an Issue](https://github.com/Hosseinghorbani0/ask-ai/issues)
