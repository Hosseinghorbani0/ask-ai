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
  <img src="assets/banner.svg" alt="ask-ai animated banner" width="100%">
</p>

<p align="center">
  <b>A minimal Python SDK to switch between LLM providers in one line.</b><br/>
  No frameworks. No servers. No overengineering.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)



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

## 🚫 What this project is NOT

> ❌ Not an AI framework  
> ❌ Not an API gateway  
> ❌ Not an agent memory system  

It does one thing perfectly: **Simplifying the API call to LLMs.**

---

## 🛠️ Advanced Usage

### 🧰 Developer QoL Utilities (Auto-Parsing)

<p align="center">
  <img src="assets/features.svg" alt="ask-ai features parsing banner" width="100%">
</p>
Stop writing Regex to clean up model outputs! `ask-ai` comes with built-in text processing flags:

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (Removes ```json and ``` tags)
# Perfect for extracting raw data from models that wrap everything in markdown
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (Returns ONLY the code block, ignores conversational filler)
# Great for automation pipelines
code = ai.ask("Write a python ping script", code=True).text

# 3. Strip Tags (Removes <think> blocks and HTML)
# Essential for reasoning models like DeepSeek-R1
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (Directly returns a Parsed Python Dictionary)
# Adds JSON instructions to the prompt and safely runs json.loads()
data_dict = ai.ask("Extract user info", json=True).json
print(data_dict['name'])
```

### 🔄 Built-in Retries & Timeout (Resiliency)

<p align="center">
  <img src="assets/resiliency.svg" alt="ask-ai resiliency banner" width="100%">
</p>
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

### 🚀 Async Support (FastAPI / Aiogram)

`ask-ai` works perfectly in asynchronous environments:

```python
import asyncio
from ask_ai import OpenAI

async def main():
    ai = OpenAI()
    # Runs non-blocking in your event loop
    response = await ai.ask_async("What is the capital of France?")
    print(response.text)

asyncio.run(main())
```

---

### 🌊 Streaming Support (Sync & Async)

Stream responses token-by-token easily:

```python
from ask_ai import OpenAI

ai = OpenAI()

# Sync Streaming
for chunk in ai.ask_stream("Write a short story about a blue dragon"):
    print(chunk, end="", flush=True)

# Async Streaming
async def stream_example():
    async for chunk in await ai.ask_stream_async("Write a short story"):
        print(chunk, end="", flush=True)
```

---

### 🎨 Media Generation (Image & Audio)

Generate images or speech with compatible providers:

```python
from ask_ai import OpenAI

ai = OpenAI()

# Generate an Image (DALL-E)
img_response = ai.ask("A majestic lion in a neon city", output_type="image")
img_response.save("lion.png")

# Generate Speech (TTS)
audio_response = ai.ask("Hello, this is a generated voice.", output_type="audio")
audio_response.save("welcome.mp3")
```

---

### 🔗 Provider Fallback

Never experience downtime by supplying alternative fallback providers:

```python
from ask_ai import OpenAI, Groq

ai = OpenAI()

# If OpenAI fails or rate-limits, it automatically switches to Groq
response = ai.ask("Explain quantum physics", providers=[ai, Groq])
print(response.text)
```

---

### 📋 Structured Output (Pydantic Support)

Force LLMs to strictly respond matching a Pydantic schema:

```python
from pydantic import BaseModel
from ask_ai import OpenAI

class User(BaseModel):
    name: str
    age: int

ai = OpenAI()
response = ai.ask("Extract name: Alice is 30 years old.", response_model=User)

user = response.pydantic
print(user.name)  # "Alice"
print(user.age)   # 30
```

---

## 🗺️ Roadmap

<<<<<<< HEAD
- [x] OpenAI, Groq, Gemini, Anthropic, Azure, OpenRouter support
- [x] Text to Image (DALL-E) and Text to Audio
- [x] Automated Retry & Timeout controls
- [x] Async Support (`await ask_async`)
- [x] Provider Fallback (`ask(..., providers=[OpenAI, Groq])`)
- [x] Streaming Support (`ask_stream`)
- [x] Structured Output (Pydantic Support)
=======
### 🚀 Roadmap 2.0 (Active)
- [x] Provider Fallback chaining & Pydantic Structured Output support
- [ ] Multi-Modal Vision input (image to text) for all key providers
- [ ] Native support for tools/function calling execution
- [ ] Memory buffer / session-based conversation management

### 🏁 Roadmap 1.0 (Completed)
- ~~[x] OpenAI, Groq, Gemini, Anthropic, Azure, OpenRouter support~~
- ~~[x] Text to Image (DALL-E) and Text to Audio~~
- ~~[x] Automated Retry & Timeout controls~~
- ~~[x] Async Support (`await ask_async`)~~
- ~~[x] Streaming Support (`ask_stream` / `ask_stream_async`)~~
- ~~[x] Provider Fallback (`ask(..., providers=[OpenAI, Groq])`)~~
- ~~[x] Structured Output (Pydantic Support)~~
>>>>>>> f0f7c6f (release: v0.4.1 - added OpenRouter image generation, fallback, structured output)

---

## 🔗 Important Links

- **PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **GitHub Repository**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (Star us! ⭐)
- **Official Website**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
- **Bug Tracker**: [Report an Issue](https://github.com/Hosseinghorbani0/ask-ai/issues)
