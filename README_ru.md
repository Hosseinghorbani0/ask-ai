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

**ИИ стал простым.**
Подключайтесь к OpenAI, Groq, Google, Anthropic и другим одной строкой кода.

> Перестаньте переписывать код ИИ для каждого провайдера. Используйте одну строку. Переключайте модели в любой момент.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Почему easyai?

- **Нет привязки к SDK**: Не учите 5 разных библиотек. Выучите одну.
- **Единый API**: `ai.ask()` работает для текста, изображений и аудио у всех провайдеров.
- **Готов к продакшену**: Встроенная безопасность типов, обработка ошибок и управление окружением.
- **Zero-Config**: Автоматически обнаруживает API ключи из вашего окружения.

---

## 🚀 Золотой пример (The Golden Example)

Посмотрите на мощь `easyai` в 3 строках кода:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "Объясни квантовые вычисления одним предложением."

# Мгновенное переключение провайдеров
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 Установка

```bash
pip install easyai
```

---

## 📖 Руководство по быстрому старту

### 1. Настройка
Экспортируйте ваши API ключи (или передайте их явно).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Стандартное использование
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("Привет, мир!"))
```

### 3. Продвинутое использование (Профессиональное)
Управляйте `temperature`, `top_p` и системными персонами (`prompt`) для профессиональных результатов.

```python
ai.advanced(
    temperature=0.7,
    prompt="Ты старший DevOps инженер."
)

print(ai.ask("Как оптимизировать Dockerfile?"))
```

---

## 🔌 Поддерживаемые провайдеры

| Провайдер | Класс | Набор функций |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | Все модели (GPT-4o, o1, и т.д.) |
| **Anthropic** | `Anthropic` | Все модели (Claude 3.5, Opus) |
| **Google** | `Google` | Все модели (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | Все модели (Llama 3, Mixtral) |
| **Azure** | `Azure` | Все модели (Enterprise) |
| **OpenRouter**| `OpenRouter`| Все модели (100+) |

---

## ⭐ Поддержите проект

Если этот проект сэкономил вам время, пожалуйста, поставьте звезду на GitHub! Это помогает нам расти.

**[Поставить звезду!](https://github.com/Hosseinghorbani0/easyai)**

---
*Создано [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*
