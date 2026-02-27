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

<p align="center" dir="rtl">
  <b>حزمة SDK بسيطة لبايثون للتبديل بين موفري خدمات الذكاء الاصطناعي بسطر برمجي واحد.</b><br/>
  بدون إطارات عمل معقدة. بدون خوادم. بدون تعقيد.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ البدء السريع (في ٥ ثوانٍ)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# يتم قراءة OPENAI_API_KEY من البيئة تلقائياً
OpenAI().ask("اشرح الثقوب السوداء لطفل عمره 5 سنوات").text

# التبديل بين الموفّرين بلحظة
Groq().ask("اشرح الثقوب السوداء لطفل عمره 5 سنوات").text
```

---

## 🧐 لماذا askai-python؟

- **دالة واحدة**: فقط اتصل بـ `.ask()`.
- **موفّرون متعددون**: دعم لـ OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter.
- **بدون إعدادات**: يتم استخراج المفاتيح تلقائياً من نظام التشغيل.
- **مجرد أداة SDK وليس إطار عمل**: لا يتدخل في بنية مشروعك.

## 🚫 ماذا لا يمثل هذا المشروع؟

> ❌ ليس إطار عمل ضخماً للذكاء الاصطناعي
> ❌ ليس نظام عبور (API Gateway)
> ❌ ليس نظام ذاكرة لـ Agent

هذا المشروع مصمم للقيام بمهمة واحدة بشكل مثالي: **تبسيط الاتصال بـ LLMs.**

---

## 🛠️ الاستخدام المتقدم

### 🧰 أدوات المطورين (Auto-Parsing)

<p align="center">
  <img src="../assets/features.svg" alt="askai-python features parsing banner" width="100%">
</p>
توقف عن كتابة تعبيرات برمجية (Regex) لتنظيف مخرجات النماذج! أدوات التنظيف مدمجة الآن:

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (إزالة أكواد مثل ```json وما شابه ذلك)
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (استخراج كود البرمجة الصافي فقط وتجاهل المحادثة الإضافية)
code = ai.ask("Write a python script", code=True).text

# 3. Strip Tags (إزالة كل وسوم الـ HTML والـ <think> من الإجابة)
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (إرجاع قاموس بايثون جاهز مباشرة من مخرجات النموذج)
data_dict = ai.ask("Extract info", json=True).json
print(data_dict['name'])
```

### 🔄 المحاولة التلقائية ومهلة الاتصال (Resiliency)

<p align="center">
  <img src="../assets/resiliency.svg" alt="askai-python resiliency banner" width="100%">
</p>
يدير التوقفات وبطء الشبكة بذكاء مع تقنية التأخير التدريجي (Exponential Backoff):

```python
# إعادة المحاولة حتى 3 مرات عند انقطاع الشبكة، مع مهلة 10 ثوانٍ
response = ai.ask("اكتب كود بايثون", retry=3, timeout=10)
```

### ⚙ إعدادات النظام 
إعداد الدور الخاص بنظام النموذج ومستوى الإبداع (Temperature) بسهولة:

```python
ai.advanced(
    temperature=0.7,
    prompt="أنت مهندس عمليات تطوير برمجيات خبير."
)

print(ai.ask("كيف يمكنني تحسين ملف الـ Dockerfile؟").text)
```

---

## 🔗 الروابط المهمة

- **مستودع جيت هاب**: [Hosseinghorbani0/askai-python](https://github.com/Hosseinghorbani0/askai-python) (لا تنسَ إضافة نجمة! ⭐)
- **حزمة PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **الموقع الرسمي**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
