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
  <b>یک SDK مینیمال پایتون برای جابجایی بین سرویس‌های هوش مصنوعی فقط با یک خط کد.</b><br/>
  بدون فریم‌ورک اضافه. بدون نیاز به سرور. بدون پیچیدگی.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ شروع سریع (در ۵ ثانیه)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# کلید OPENAI_API_KEY را به طور خودکار از محیط می‌خواند
OpenAI().ask("سیاه‌چاله‌ها را مثل یک کودک ۵ ساله توضیح بده").text

# تغییر سرویس‌دهنده به صورت آنی
Groq().ask("سیاه‌چاله‌ها را مثل یک کودک ۵ ساله توضیح بده").text
```

---

## 🧐 چرا ask-ai؟

- **یک تابع ساده**: فقط کافیست `.ask()` را صدا بزنید.
- **سرویس‌های متعدد**: پشتیبانی از OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter.
- **بدون پیکربندی (Zero Config)**: کلیدهای API مستقیماً از متغیرهای سیستم عامل خوانده می‌شوند.
- **یک SDK، نه یک فریم‌ورک**: در معماری و کد شما دخالت نمی‌کند.

## ⚖️ مقایسه با سایر ابزارها

| ویژگی | ask-ai | LangChain |
| -------------- | ------ | --------- |
| زمان راه‌اندازی | ۳۰ ثانیه | ۱+ ساعت |
| منحنی یادگیری (سختی) | ⭐ | ⭐⭐⭐⭐⭐ |
| پشتیبانی از Async | ⏳ *(به زودی)* | ⚠️ پیچیده |
| تلاش مجدد/تایم‌اوت | ✅ داخلی | ❌ دستی |
| نیاز به Gateway | ❌ خیر | ❌ خیر |
| خط کد برای تغییر سرویس | **۱** | ۲۰+ |

## 🚫 این پروژه چه چیزی نیست؟

> ❌ یک فریم‌ورک بزرگ هوش مصنوعی نیست.
> ❌ یک API Gateway نیست.
> ❌ یک سیستم حافظه Agent نیست.

این پروژه فقط یک کار را به بهترین نحو انجام می‌دهد: **ساده‌سازی تماس API با LLMها.**

---

## 🛠️ استفاده پیشرفته

### مقاومت داخلی (Retries & Timeout)
مدیریت هوشمند خطاهای اینترنت و محدودیت‌های سرعت (`429`) با تکنیک تاخیر تصاعدی (Exponential Backoff):

```python
from ask_ai import OpenAI
ai = OpenAI()

# در صورت بروز خطای شبکه تا ۳ بار تلاش مجدد می‌کند (با تایم‌اوت ۱۰ ثانیه)
response = ai.ask("یک اسکریپت پایتون بنویس", retry=3, timeout=10)
```

### پیکربندی سیستم 
تنظیم نقش سیستم و درجه حرارت به صورت مستقیم:

```python
ai.advanced(
    temperature=0.7,
    prompt="You are a senior DevOps engineer."
)

print(ai.ask("How do I optimize a Dockerfile?").text)
```

---

## 🗺️ نقشه راه (Roadmap)

- [x] پشتیبانی از سرویس‌دهنده‌های برتر
- [x] تبدیل متن به عکس و صوت
- [x] کنترل‌کننده‌های داخلی سعی مجدد و Timeout
- [ ] توابع حالت غیرهمزمان (`await ask_async`)
- [ ] لیست سرویس‌های جایگزین (`ask(..., providers=[OpenAI, Groq])`)
- [ ] پشتیبانی از خروجی‌های ساختاریافته JSON (Pydantic Support)

---

## 🔗 لینک‌های مهم

- **مخزن گیت‌هاب**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (ستاره فراموش نشود! ⭐)
- **پکیج PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **وب‌سایت رسمی**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
