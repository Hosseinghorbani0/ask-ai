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
  <img src="../assets/banner.svg" alt="askai-python animated banner" width="100%">
</p>

<p align="center">
  <b>Минималистичный Python SDK для переключения между AI-провайдерами одной строкой кода.</b><br/>
  Никаких фреймворков. Никаких серверов. Никакой избыточности.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Быстрый старт (За 5 секунд)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Автоматически считывает OPENAI_API_KEY из среды
OpenAI().ask("Объясни чёрные дыры как для 5-летнего").text

# Мгновенное переключение провайдеров
Groq().ask("Объясни чёрные дыры как для 5-летнего").text
```

---

## 🧐 Почему askai-python?

- **Одна функция**: Просто вызовите `.ask()`.
- **Поддержка множества провайдеров**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter.
- **Нулевая конфигурация**: Ключи автоматически загружаются из переменных операционной системы.
- **Сначала SDK, а не фреймворк**: Никак не вмешивается в вашу архитектуру и код.

## 🚫 Чем этот проект НЕ является?

> ❌ Это НЕ огромный AI фреймворк.
> ❌ Это НЕ API шлюз (API Gateway).
> ❌ Это НЕ система памяти для агентов.

Этот проект идеально делает только одну вещь: **Упрощает API-запросы к LLM.**

---

## 🛠️ Продвинутое использование

### 🧰 Инструменты для разработчиков (Auto-Parsing)

<p align="center">
  <img src="../assets/features.svg" alt="askai-python features parsing banner" width="100%">
</p>
Больше не нужно писать Regex для очистки вывода! `askai-python` содержит встроенные флаги:

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (Удаляет теги ```json и т. д.)
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (Возвращает ТОЛЬКО блок кода, игнорируя болтовню)
code = ai.ask("Write a python script", code=True).text

# 3. Strip Tags (Удаляет блоки <think> и HTML-теги)
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (Напрямую возвращает словарь Python)
data_dict = ai.ask("Extract info", json=True).json
print(data_dict['name'])
```

### 🔄 Встроенные повторные попытки и таймаут (Resiliency)

<p align="center">
  <img src="../assets/resiliency.svg" alt="askai-python resiliency banner" width="100%">
</p>
Умная обработка ошибок сети и ограничений скорости (`429`) с экспоненциальной задержкой:

```python
# Повторяет попытку до 3 раз при ошибках сети с таймаутом в 10 секунд
response = ai.ask("Напиши python скрипт", retry=3, timeout=10)
```

### ⚙ Настройка системы
Прямая установка системной роли и креативности (temperature):

```python
ai.advanced(
    temperature=0.7,
    prompt="Вы — старший инженер DevOps."
)

print(ai.ask("Как мне оптимизировать Dockerfile?").text)
```

---

## 🔗 Важные ссылки

- **GitHub-репозиторий**: [Hosseinghorbani0/askai-python](https://github.com/Hosseinghorbani0/askai-python) (Не забудьте поставить звезду! ⭐)
- **PyPI пакет**: [askai-python](https://pypi.org/project/askai-python/)
- **Официальный сайт**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
