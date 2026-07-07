# askai-python 🚀

**A minimal Python SDK to switch between LLM providers in one line.**  
No frameworks. No servers. No overengineering.

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-View%20Source-blue.svg)](https://github.com/Hosseinghorbani0/askai-python)

---

## ⚡ Quick Start (5 seconds)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Auto-detects OPENAI_API_KEY from environment
print(OpenAI().ask("Explain black holes like I'm 5").text)

# Switch provider instantly
print(Groq().ask("Explain black holes like I'm 5").text)
```

---

## 🧐 Why askai-python?

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
  <img src="https://raw.githubusercontent.com/Hosseinghorbani0/askai-python/main/assets/features.svg" alt="askai-python features parsing banner" width="100%">
</p>
Stop writing Regex to clean up model outputs! `askai-python` comes with built-in text processing flags:

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

## 🚀 Built-in Resiliency (Retries & Timeouts)

<p align="center">
  <img src="https://raw.githubusercontent.com/Hosseinghorbani0/askai-python/main/assets/resiliency.svg" alt="askai-python resiliency banner" width="100%">
</p>

Build reliable apps without writing your own loops. `askai-python` handles rate limits (`429`) and network drops via an internal exponential backoff.

```python
from ask_ai import OpenAI

ai = OpenAI()

# Automatically retries up to 3 times on transient errors, with a 15-second timeout
response = ai.ask(
    "Write a complex python script", 
    retry=3, 
    timeout=15 
)
```

## 🎨 Media Generation (Image & Audio)

Generate images or speech with compatible providers:

```python
from ask_ai import OpenAI

ai = OpenAI()

# Generate an Image (DALL-E)
img_response = ai.ask("A majestic lion in a neon city", output_type="image")
img_response.save("lion.png")

# Generate Speech (TTS)
audio_response = ai.ask("Hello, this is a voice.", output_type="audio")
audio_response.save("welcome.mp3")
```

## 🔗 Provider Fallback

Never experience downtime by supplying fallback providers:

```python
from ask_ai import OpenAI, Groq

ai = OpenAI()
response = ai.ask("Explain quantum physics", providers=[ai, Groq])
print(response.text)
```

## 📋 Structured Output (Pydantic Support)

Force LLMs to strictly respond matching a Pydantic schema:

```python
from pydantic import BaseModel
from ask_ai import OpenAI

class User(BaseModel):
    name: str
    age: int

ai = OpenAI()
response = ai.ask("Extract name: Alice is 30.", response_model=User)
user = response.pydantic
print(user.name)  # "Alice"
```

## 🔌 Supported Providers

| Provider | Class | Capabilities |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | Text, Images (DALL-E), Vision |
| **Anthropic** | `Anthropic` | Text, Vision (Claude 3.5) |
| **Google** | `Google` | Text, Images, Video, Audio |
| **Groq** | `Groq` | Ultra-fast Llama 3 & Mixtral |
| **Azure** | `Azure` | Enterprise-grade OpenAI |
| **OpenRouter**| `OpenRouter`| 100+ community models |

---

## 🗺️ Roadmap

### 🚀 Roadmap 2.0 (Active)
- [x] Provider Fallback chaining & Pydantic Structured Output support
- [ ] Multi-Modal Vision input (image to text) for all key providers
- [ ] Native support for tools/function calling execution
- [ ] Memory buffer / session-based conversation management

### 🏁 Roadmap 1.0 (Completed)
- ~~[x] Baseline multiple providers~~
- ~~[x] Automated Retry & Timeout controls~~
- ~~[x] Async API (`await ask_async`)~~
- ~~[x] Streaming Support (`ask_stream` / `ask_stream_async`)~~
- ~~[x] Provider Fallback (`fallback=[Groq()]`)~~
- ~~[x] Structured Outputs (Pydantic Support)~~

---

## 🔗 Important Links

- **GitHub Repository**: [Hosseinghorbani0/askai-python](https://github.com/Hosseinghorbani0/askai-python) (Star us! ⭐)
- **Official Website**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
- **Bug Tracker**: [Report an Issue](https://github.com/Hosseinghorbani0/askai-python/issues)
