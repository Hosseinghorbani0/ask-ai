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

**AI Made Simple.**
只需一行代码即可连接到 OpenAI、Groq、Google、Anthropic 等。

> 停止为每个提供商重写 AI 代码。只用一行。随时切换模型。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ 为什么选择 easyai？

- **无 SDK 锁定**：不要学习 5 个不同的库。只学一个。
- **统一 API**：`ai.ask()` 适用于所有提供商的文本、图像和音频。
- **生产就绪**：内置类型安全、错误处理和环境管理。
- **零配置**：自动检测环境中的 API 密钥。

---

## 🚀 黄金示例 (The Golden Example)

用 3 行代码见证 `easyai` 的力量：

```python
from easyai import OpenAI, Anthropic, Google

prompt = "用一句话解释量子计算。"

# 即时切换提供商
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 安装

```bash
pip install easyai
```

---

## 📖 快速入门指南

### 1. 设置
导出您的 API 密钥（或显式传递它们）。
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. 标准用法
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("你好，世界！"))
```

### 3. 高级用法 (专业)
控制 `temperature`、`top_p` 和系统角色 (`prompt`) 以获得专业结果。

```python
ai.advanced(
    temperature=0.7,
    prompt="你是一名高级 DevOps 工程师。"
)

print(ai.ask("如何优化 Dockerfile？"))
```

---

## 🔌 支持的提供商

| 提供者 | Class | 功能集 |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | 所有模型 (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | 所有模型 (Claude 3.5, Opus) |
| **Google** | `Google` | 所有模型 (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | 所有模型 (Llama 3, Mixtral) |
| **Azure** | `Azure` | 所有部署 (Enterprise) |
| **OpenRouter**| `OpenRouter`| 所有模型 (100+) |

---

## ⭐ 支持本项目

如果这个项目为您节省了时间，请考虑在 GitHub 上给它一颗星！这有助于我们成长。

**[给它一颗星！](https://github.com/Hosseinghorbani0/easyai)**

---
*由 [Hossein Ghorbani](https://hosseinghorbani0.ir/) 构建 | [GitHub](https://github.com/Hosseinghorbani0)。*
