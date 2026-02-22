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

<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ask-AI SVG Banner Preview</title>
    <style>
        body {
            background-color: #0d1117;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
        }
        /* این استایل فقط برای نمایش بهتر در پیش‌نمایش است */
        .svg-wrapper {
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            border-radius: 12px;
        }
    </style>
</head>
<body>

    <div class="svg-wrapper">
        <!-- از خط پایین (تگ svg) تا انتهای آن را برای پروژه خود کپی کنید -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 280" width="100%" height="100%">
            <defs>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&amp;display=swap');
                    
                    text {
                        font-family: 'Fira Code', 'Courier New', Courier, monospace;
                        font-size: 15px;
                    }
                    
                    .bg { fill: #0d1117; rx: 12px; }
                    .header { fill: #161b22; }
                    
                    /* Mac Window Controls */
                    .mac-red { fill: #ff5f56; }
                    .mac-yellow { fill: #ffbd2e; }
                    .mac-green { fill: #27c93f; }
                    
                    /* Syntax Highlighting (GitHub Dark Theme) */
                    .text-plain { fill: #c9d1d9; }
                    .text-keyword { fill: #ff7b72; font-weight: 500; }
                    .text-class { fill: #d2a8ff; font-weight: 600; }
                    .text-string { fill: #a5d6ff; }
                    .text-comment { fill: #8b949e; font-style: italic; }
                    .text-boolean { fill: #79c0ff; }
                    
                    /* Animations for Provider Switching */
                    .state-1 { animation: fade1 12s infinite; }
                    .state-2 { animation: fade2 12s infinite; }
                    .state-3 { animation: fade3 12s infinite; }

                    @keyframes fade1 {
                        0%, 25% { opacity: 1; }
                        30%, 95% { opacity: 0; }
                        100% { opacity: 1; }
                    }
                    @keyframes fade2 {
                        0%, 25% { opacity: 0; }
                        30%, 58% { opacity: 1; }
                        63%, 100% { opacity: 0; }
                    }
                    @keyframes fade3 {
                        0%, 58% { opacity: 0; }
                        63%, 90% { opacity: 1; }
                        95%, 100% { opacity: 0; }
                    }

                    /* Blinking Cursor */
                    .cursor {
                        fill: #c9d1d9;
                        animation: blink 1s step-end infinite;
                    }
                    @keyframes blink {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0; }
                    }
                </style>
            </defs>

            <!-- Window Background -->
            <rect width="750" height="280" class="bg" />
            
            <!-- Window Header -->
            <path d="M0 12 Q 0 0 12 0 L 738 0 Q 750 0 750 12 L 750 40 L 0 40 Z" class="header" />
            <circle cx="20" cy="20" r="6" class="mac-red" />
            <circle cx="40" cy="20" r="6" class="mac-yellow" />
            <circle cx="60" cy="20" r="6" class="mac-green" />
            <text x="375" y="25" fill="#8b949e" font-size="13px" text-anchor="middle" font-family="sans-serif">ask_ai_demo.py</text>

            <!-- Code Content Container -->
            <g transform="translate(30, 80)">
                
                <!-- STATE 1: OpenAI -->
                <g class="state-1">
                    <text y="0">
                        <tspan class="text-keyword">from</tspan><tspan class="text-plain"> ask_ai </tspan><tspan class="text-keyword">import</tspan><tspan class="text-class"> OpenAI</tspan>
                    </text>
                    <text y="35" class="text-comment"># Switch providers in one line. Zero extra configuration.</text>
                    <text y="70">
                        <tspan class="text-plain">ai = </tspan><tspan class="text-class">OpenAI</tspan><tspan class="text-plain">()</tspan>
                    </text>
                    <text y="105">
                        <tspan class="text-plain">answer = ai.ask(</tspan><tspan class="text-string">"Write a ping script"</tspan><tspan class="text-plain">, code=</tspan><tspan class="text-boolean">True</tspan><tspan class="text-plain">)</tspan>
                    </text>
                    <text y="145" class="text-comment"># 🚀 Generated by GPT-4o: Pure python code extracted cleanly!</text>
                </g>

                <!-- STATE 2: Groq -->
                <g class="state-2">
                    <text y="0">
                        <tspan class="text-keyword">from</tspan><tspan class="text-plain"> ask_ai </tspan><tspan class="text-keyword">import</tspan><tspan class="text-class"> Groq</tspan>
                    </text>
                    <text y="35" class="text-comment"># Switch providers in one line. Zero extra configuration.</text>
                    <text y="70">
                        <tspan class="text-plain">ai = </tspan><tspan class="text-class">Groq</tspan><tspan class="text-plain">()</tspan>
                    </text>
                    <text y="105">
                        <tspan class="text-plain">answer = ai.ask(</tspan><tspan class="text-string">"Write a ping script"</tspan><tspan class="text-plain">, code=</tspan><tspan class="text-boolean">True</tspan><tspan class="text-plain">)</tspan>
                    </text>
                    <text y="145" class="text-comment"># ⚡ Generated by Llama-3 (Groq): Pure python code extracted cleanly!</text>
                </g>

                <!-- STATE 3: Gemini -->
                <g class="state-3">
                    <text y="0">
                        <tspan class="text-keyword">from</tspan><tspan class="text-plain"> ask_ai </tspan><tspan class="text-keyword">import</tspan><tspan class="text-class"> Gemini</tspan>
                    </text>
                    <text y="35" class="text-comment"># Switch providers in one line. Zero extra configuration.</text>
                    <text y="70">
                        <tspan class="text-plain">ai = </tspan><tspan class="text-class">Gemini</tspan><tspan class="text-plain">()</tspan>
                    </text>
                    <text y="105">
                        <tspan class="text-plain">answer = ai.ask(</tspan><tspan class="text-string">"Write a ping script"</tspan><tspan class="text-plain">, code=</tspan><tspan class="text-boolean">True</tspan><tspan class="text-plain">)</tspan>
                    </text>
                    <text y="145" class="text-comment"># 🧠 Generated by Gemini-1.5: Pure python code extracted cleanly!</text>
                </g>

                <!-- Blinking Cursor -->
                <rect x="0" y="165" width="10" height="18" class="cursor" />
            </g>
        </svg>
        <!-- پایان کد SVG -->
    </div>
</body>
</html>

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
