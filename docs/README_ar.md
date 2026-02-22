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

<p align="center" dir="rtl">
  <b>حزمة تطوير (SDK) بسيطة بلغة بايثون للتبديل بين مزودي الذكاء الاصطناعي (LLM) في سطر واحد.</b><br/>
  بدون أطر عمل. بدون خوادم. بدون تعقيد هندسي.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

<div dir="rtl">

## ⚡ البداية السريعة (في 5 ثوانٍ)

</div>

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# يتم اكتشاف OPENAI_API_KEY تلقائياً من البيئة
OpenAI().ask("اشرح الثقوب السوداء وكأنني في الخامسة من عمري").text

# قم بتبديل المزود في لمح البصر
Groq().ask("اشرح الثقوب السوداء وكأنني في الخامسة من عمري").text
```

---

<div dir="rtl">

## 🧐 لماذا ask-ai؟

- **وظيفة واحدة**: فقط استدعِ `.ask()`
- **مزودون متعددون**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **تكوين صفري**: يتم سحب المفاتيح من بيئة النظام تلقائياً.
- **SDK أولاً، وليس إطار عمل**: لا يعيق عملك أو يفرض عليك بنية معينة.

## ⚖️ المقارنة

| الميزة | ask-ai | LangChain |
| -------------- | ------ | --------- |
| وقت الإعداد | 30 ثانية | ساعة واحدة |
| منحنى التعلم | ⭐ | ⭐⭐⭐⭐⭐ |
| دعم التزامن (Async) | ⏳ *(قريباً)* | ⚠️ معقد |
| إعادة المحاولة/المهلة | ✅ مدمج | ❌ يدوي |
| الحاجة إلى Gateway | ❌ لا | ❌ لا |
| الأسطر لتغيير المزود | **1** | 20+ |

## 🚫 ما الذي ليس عليه هذا المشروع

> ❌ ليس إطار عمل ذكاء اصطناعي (AI Framework)
> ❌ ليس بوابة وصول (API Gateway)
> ❌ ليس نظام ذاكرة للعملاء (Agent System)

إنه يقوم بشيء واحد بامتياز: **تبسيط استدعاء الـ API للنماذج اللغوية (LLMs).**

---

## 🛠️ الاستخدام المتقدم

### المرونة المدمجة (Retries & Timeout)
تعامل مع حدود المعدل (`429`) وانقطاع الشبكة تلقائياً:

```python
from ask_ai import OpenAI
ai = OpenAI()

# سيعيد المحاولة حتى 3 مرات في حال أخطاء الشبكة، مع مهلة 10 ثوانٍ افتراضياً
response = ai.ask("اكتب كود بايثون متقدم", retry=3, timeout=10)
```

### تكوين النظام (System Configuration)
قم بتعيين رسائل النظام ودرجة الحرارة (Temperature) مباشرة:

```python
ai.advanced(
    temperature=0.7,
    prompt="أنت مهندس DevOps أول."
)

print(ai.ask("كيف أقوم بتحسين ملف Dockerfile؟").text)
```

---

## 🔗 روابط هامة

- **مستودع GitHub**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (امنحنا نجمة ⭐)
- **موقع PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **الموقع الرسمي**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)

</div>
