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

**الذكاء الاصطناعي أصبح بسيطاً.**
اتصل بـ OpenAI و Groq و Google و Anthropic والمزيد بسطر واحد من التعليمات البرمجية.

> توقف عن إعادة كتابة كود الذكاء الاصطناعي لكل مزود. استخدم سطراً واحداً. بدّل النماذج في أي وقت.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ لماذا easyai؟

- **بدون قفل SDK**: لا تتعلم 5 مكتبات مختلفة. تعلم واحدة.
- **واجهة موحدة**: `ai.ask()` تعمل للنصوص والصور والصوت عبر جميع المزودين.
- **جاهز للإنتاج**: أمان النوع المدمج، معالجة الأخطاء، وإدارة البيئة.
- **بدون تكوين (Zero-Config)**: الكشف التلقائي عن مفاتيح API من بيئتك.

---

## 🚀 المثال الذهبي (The Golden Example)

شاهد قوة `easyai` في 3 أسطر من الكود:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "اشرح الحوسبة الكمومية في جملة واحدة."

# بدّل المزودين فوراً
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 التثبيت

```bash
pip install easyai
```

---

## 📖 دليل البدء السريع

### 1. الإعداد
قم بتصدير مفاتيح API الخاصة بك (أو مررها بشكل صريح).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. الاستخدام القياسي
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("مرحباً بالعالم!"))
```

### 3. الاستخدام المتقدم (احترافي)
تحكم في `temperature` و `top_p` وشخصيات النظام (`prompt`) للحصول على نتائج احترافية.

```python
ai.advanced(
    temperature=0.7,
    prompt="أنت مهندس DevOps أول."
)

print(ai.ask("كيف أقوم بتحسين Dockerfile؟"))
```

---

## 🔌 المزودون المدعومين

| المزود | الفئة | مجموعة الميزات |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | جميع الموديلات (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | جميع الموديلات (Claude 3.5, Opus) |
| **Google** | `Google` | جميع الموديلات (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | جميع الموديلات (Llama 3, Mixtral) |
| **Azure** | `Azure` | جميع الموديلات (Enterprise) |
| **OpenRouter**| `OpenRouter`| جميع الموديلات (100+) |

---

## ⭐ ادعم المشروع

إذا وفر هذا المشروع وقتك، يرجى التفكير في إعطائه نجمة على GitHub! هذا يساعدنا على النمو.

**[أعطه نجمة!](https://github.com/Hosseinghorbani0/easyai)**

---
*تم بناؤه بواسطة [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*

</div>
