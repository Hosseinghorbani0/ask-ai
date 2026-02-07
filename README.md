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

<p align="center">
  <b>AI Made Simple.</b><br/>
  One unified Python client for OpenAI, Claude, Gemini, Groq & more.
</p>

> Stop rewriting AI code for every provider. Use one line. Switch models anytime.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Why easyai?

- **No SDK lock-in**: Don't learn 5 different libraries. Learn one.
- **Unified API**: `ai.ask()` works for text, images, and audio across all providers.
- **Production Ready**: Built-in type safety, error handling, and environment management.
- **Zero-Config**: Auto-detects API keys from your environment.

---

## 🚀 The Golden Example

See the power of `easyai` in 3 lines of code:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "Explain quantum computing in one sentence."

# Switch providers instantly
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 Installation

```bash
pip install easyai
```

---

## 📖 Quick Start

### 1. Setup
Export your API keys (or pass them explicitly).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Standard Usage
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("Hello, World!"))
```

### 3. Advanced Usage
Control `temperature`, `top_p`, and system personas for professional results.
```python
ai.advanced(
    temperature=0.7,
    prompt="You are a senior DevOps engineer."
)

print(ai.ask("How do I optimize a Dockerfile?"))
```

---

## 🔌 Supported Providers

| Provider | Class | Feature Set |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | All Models (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | All Models (Claude 3.5, Opus) |
| **Google** | `Google` | All Models (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | All Models (Llama 3, Mixtral) |
| **Azure** | `Azure` | All Deployments |
| **OpenRouter**| `OpenRouter`| All Models (100+) |

---

## ⭐ Support the Project

If this project saved you time, please consider giving it a star on GitHub! It helps us grow.

**[Give it a Star!](https://github.com/Hosseinghorbani0/easyai)**

---
*Built by [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*
