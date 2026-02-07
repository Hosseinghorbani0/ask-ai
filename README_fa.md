<div dir="rtl">

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

**هوش مصنوعی، ساده‌تر از همیشه.**
تنها با یک خط کد به OpenAI, Groq, Google, Anthropic و سرویس‌های دیگر متصل شوید.

> دست از بازنویسی کد برای هر سرویس هوش مصنوعی بردارید. فقط بپرسید (`ask`).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ چرا easyai؟

- **بدون وابستگی (SDK Lock-in)**: ۵ کتابخانه مختلف یاد نگیرید. یکی یاد بگیرید.
- **رابط کاربری واحد**: متد `ai.ask()` برای متن، تصویر و صدا در همه سرویس‌ها کار می‌کند.
- **آماده برای پروداکشن**: مدیریت خطا، تایپ‌سیف و تنظیمات محیطی داخلی.
- **بدون تنظیمات (Zero-Config)**: تشخیص خودکار API Key از سیستم.

---

## 🚀 مثال طلایی (The Golden Example)

قدرت `easyai` را در ۳ خط ببینید:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "رایانش کوانتومی را در یک جمله توضیح بده."

# سوئیچ آنی بین سرویس‌ها+
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 نصب

```bash
pip install easyai
```

---

## 📖 راهنمای شروع سریع

### ۱. تنظیمات
کلیدهای API خود را اکسپورت کنید (یا مستقیم پاس دهید).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### ۲. استفاده استاندارد
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("سلام دنیا!"))
```

### ۳. استفاده پیشرفته (حرفه‌ای)
کنترل `temperature`، `top_p` و پرسونای سیستم (`prompt`) برای نتایج حرفه‌ای.

```python
ai.advanced(
    temperature=0.7,
    prompt="تو یک مهندس ارشد دواپس (DevOps) هستی."
)

print(ai.ask("چطور یک Dockerfile را بهینه کنم؟"))
```

---

## 🔌 سرویس‌های پشتیبانی شده

| سرویس‌دهنده | کلاس | قابلیت‌ها |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | تمام مدل‌ها (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | تمام مدل‌ها (Claude 3.5, Opus) |
| **Google** | `Google` | تمام مدل‌ها (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | تمام مدل‌ها (Llama 3, Mixtral) |
| **Azure** | `Azure` | تمام مدل‌ها (Enterprise) |
| **OpenRouter**| `OpenRouter`| تمام مدل‌ها (100+) |

---

## ⭐ حمایت از پروژه

اگر این پروژه در زمان شما صرفه‌جویی کرده، لطفاً به آن در گیت‌هاب ستاره بدهید! این کار به رشد ما کمک می‌کند.

**[به ما ستاره بدهید!](https://github.com/Hosseinghorbani0/easyai)**

---
*ساخته شده توسط [حسین قربانی](https://hosseinghorbani0.ir/) | [گیت‌هاب](https://github.com/Hosseinghorbani0).*

</div>
