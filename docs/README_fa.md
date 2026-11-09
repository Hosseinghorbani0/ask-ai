# ask-ai

[![نسخه PyPI](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![نسخه‌های پایتون](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![مجوز MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**یک SDK کوچک و type-safe پایتون برای فراخوانی چند ارائه‌دهنده LLM با API یکسان.**
بدون نیاز به استفاده از چارچوب‌های بزرگ orchestration، آن را در اسکریپت‌ها و برنامه‌های پایتون به کار ببرید.

`ask-ai` یک کتابخانه کلاینت است، نه سرویس میزبانی‌شده یا gateway. یک کلاینت ارائه‌دهنده می‌سازید، آن را به‌صورت همگام یا ناهمگام فراخوانی می‌کنید و یک شیء مشترک `Response` می‌گیرید. SDKهای ارائه‌دهندگان اختیاری‌اند؛ فقط موارد موردنیاز را نصب کنید.

## زبان‌های مستندات

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## فهرست مطالب

- [قابلیت‌ها](#قابلیتها)
- [نیازمندی‌ها و نصب](#نیازمندیها-و-نصب)
- [ارائه‌دهندگان](#ارائهدهندگان)
- [شروع سریع](#شروع-سریع)
- [API عمومی](#api-عمومی)
- [گزینه‌های درخواست](#گزینههای-درخواست)
- [تلاش مجدد، جایگزینی و مسیریابی](#تلاش-مجدد-جایگزینی-و-مسیریابی)
- [خروجی ساخت‌یافته](#خروجی-ساختیافته)
- [استریم و استفاده ناهمگام](#استریم-و-استفاده-ناهمگام)
- [تولید رسانه و دانلود امن](#تولید-رسانه-و-دانلود-امن)
- [نشست‌ها و چرخه عمر کلاینت](#نشستها-و-چرخه-عمر-کلاینت)
- [قابلیت‌ها و مشاهده‌پذیری](#قابلیتها-و-مشاهدهپذیری)
- [معماری](#معماری)
- [رابط خط فرمان](#رابط-خط-فرمان)
- [سازگاری و عیب‌یابی](#سازگاری-و-عیبیابی)
- [مشارکت، پشتیبانی و مجوز](#مشارکت-پشتیبانی-و-مجوز)

## قابلیت‌ها

- APIهای یکپارچه `ask`، `ask_async`، `ask_stream` و `ask_stream_async`.
- جایگزینی ارائه‌دهنده و مسیریابی مبتنی بر سیاست.
- تلاش مجدد برای خطاهای گذرا، با مهلت زمانی برای هر فراخوانی و کل عملیات.
- فراداده تایپ‌شده پاسخ، مصرف نرمال‌شده توکن و hookهای اختیاری مشاهده‌پذیری.
- JSON و پاسخ ساخت‌یافته اعتبارسنجی‌شده برای ارائه‌دهندگان پشتیبانی‌شده.
- نشست گفت‌وگوی اختیاری در حافظه.
- endpointهای سازگار با OpenAI Chat Completions، از جمله سرورهای محلی.
- دانلود امن رسانه با سیاست‌های قابل تنظیم.

API عمومی درخواست در حال حاضر متن ارسال می‌کند؛ اعلام قابلیت به‌معنی پشتیبانی ورودی تصویر برای vision نیست. اجرای فراخوانی ابزارها و ذخیره‌سازی دائمی تاریخچه ارائه نمی‌شود.

## نیازمندی‌ها و نصب

- پایتون 3.10 یا جدیدتر.
- بسته اصلی وابستگی الزامی ندارد. SDKهای ارائه‌دهنده و کتابخانه‌های رسانه/خروجی ساخت‌یافته، extraهای اختیاری هستند.

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI، Azure OpenAI، OpenRouter و endpointهای سازگار
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic و jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # دانلود امن رسانه
python -m pip install "askai-python[all]"
```

اعتبارنامه‌ها را در متغیر محیطی تنظیم کنید یا هنگام ساخت ارائه‌دهنده `api_key=` بدهید. اطلاعات محرمانه را در کد منبع قرار ندهید.

## ارائه‌دهندگان

| ارائه‌دهنده | نام import | Extra | متغیر محیطی | مدل پیش‌فرض |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | تعیین deployment الزامی است |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| سازگار با OpenAI | `OpenAICompatibleProvider` | `openai` | ندارد (اختیاری) | هنگام ساخت الزامی |

Azure به `AZURE_OPENAI_ENDPOINT` نیز نیاز دارد. نام deployment را با `model=` یا `AZURE_OPENAI_DEPLOYMENT_NAME` تعیین کنید. مقدار پیش‌فرض `AZURE_OPENAI_API_VERSION` برابر `2024-06-01` است. ارائه‌دهنده سازگار به `base_url` مطلق HTTP(S) و مدل نیاز دارد؛ برای endpointهای محلی می‌توان `api_key` را حذف کرد.

`capabilities()` پشتیبانی اعلام‌شده از متن، استریم، استریم ناهمگام، خروجی ساخت‌یافته، فراخوانی ابزار، تولید تصویر/صدا و vision را برمی‌گرداند. این اطلاعات تضمین نمی‌کند که مدل یا حساب مشخصی همه قابلیت‌ها را فعال داشته باشد. اجرای ابزار و ورودی vision به‌عنوان قابلیت عمومی درخواست ارائه نمی‌شوند.

## شروع سریع

```python
from ask_ai import OpenAI

client = OpenAI()  # متغیر OPENAI_API_KEY را می‌خواند
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## API عمومی

| متد | نتیجه | توضیح |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | درخواست همگام |
| `await provider.ask_async(query, **options)` | `Response` | درخواست ناهمگام بومی |
| `provider.ask_stream(query, **options)` | iterator رشته | استریم متن همگام |
| `async for chunk in provider.ask_stream_async(...)` | iterator ناهمگام | استریم متن ناهمگام |
| `provider.ask_stream_events(...)` | iterator رویداد | استریم همگام تایپ‌شده |
| `provider.ask_stream_events_async(...)` | iterator رویداد ناهمگام | استریم ناهمگام تایپ‌شده |

`Response` شامل `text`، متن اصلی `raw`، `json` تجزیه‌شده، و در صورت تعیین `response_model` مقادیر `parsed`/`pydantic` است؛ `media`، `usage` و `metadata` نیز اختیاری هستند. `response.json` متن را تجزیه می‌کند؛ برای درخواست JSON از `json=True` و برای اعتبارسنجی از `response_model=...` استفاده کنید.

## گزینه‌های درخواست

گزینه‌ها را به درخواست بدهید یا با `provider.advanced(...)` مقدار پیش‌فرض تعریف کنید. گزینه‌های هر درخواست اولویت دارند.

| گزینه | کاربرد |
|---|---|
| `temperature`، `max_tokens`، `top_p` | کنترل‌های متداول تولید |
| `frequency_penalty`، `presence_penalty`، `stop` | تنظیمات پشتیبانی‌شده توسط ارائه‌دهنده |
| `system_message` (نام‌های جایگزین: `system`، `prompt`) | دستور سیستم |
| `timeout` | محدودیت زمانی یک فراخوانی ارائه‌دهنده (پیش‌فرض کلاینت ۳۰ ثانیه) |
| `total_timeout` | مهلت کل عملیات، شامل تلاش‌های مجدد |
| `retry` | تعداد تلاش‌های اضافه؛ پیش‌فرض ۲ (حداکثر ۳ تلاش) |
| `json=True` | درخواست خروجی JSON و امکان تجزیه با `response.json` |
| `response_model`، `validation_retries` | تجزیه و اعتبارسنجی مدل ساخت‌یافته پشتیبانی‌شده |
| `output_type` | درخواست خروجی `image` یا `audio` پشتیبانی‌شده |
| `clean`، `strip`، `code` | پاک‌سازی/استخراج متن هنگام خواندن `response.text` |
| `strict_options=True` | خطا برای گزینه ناشناخته به‌جای هشدار |

پشتیبانی گزینه‌ها به ارائه‌دهنده و مدل بستگی دارد. گزینه ناشناخته به‌طور پیش‌فرض هشدار می‌دهد؛ حالت strict خطای `ValueError` ایجاد می‌کند. گزینه منسوخ `safe_mode` رفتار تعریف‌شده‌ای ندارد. نوع خروجی پشتیبانی‌نشده خطای صریح می‌دهد.

## تلاش مجدد، جایگزینی و مسیریابی

برای خطاهای گذرای قابل‌تکرار، به‌طور پیش‌فرض دو بار دیگر تلاش می‌شود (حداکثر سه تلاش). خطای درخواست نامعتبر و احراز هویت تکرار نمی‌شود. `Retry-After` تا سقف ۳۰ ثانیه رعایت می‌شود. `timeout` یک فراخوانی را محدود می‌کند و `total_timeout` کل عملیات را.

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

فقط در خطاهای قابل‌تکرار ارائه‌دهنده به گزینه بعدی می‌رویم. `Router` انتخاب مبتنی بر سیاست و بودجه کلی `max_attempts` را فراهم می‌کند. تلاش مجدد و جایگزینی ممکن است هزینه بیشتری داشته باشد. پس از ارسال قطعه‌ای از استریم، آن استریم تکرار نمی‌شود.

## خروجی ساخت‌یافته

مدل‌های Pydantic، dataclass، `TypedDict` و JSON Schema پشتیبانی می‌شوند. نتیجه اعتبارسنجی‌شده را از `.parsed` در شیء `Response` دریافت کنید.

```python
from pydantic import BaseModel
from ask_ai import OpenAI

class Summary(BaseModel):
    title: str
    points: list[str]

response = OpenAI().ask(
    "Summarize the water cycle.",
    response_model=Summary,
    validation_retries=1,
)
print(response.parsed.title)
```

پشتیبانی بومی ساختار در ارائه‌دهندگان متفاوت است. اعتبارسنجی محلی انجام می‌شود و خروجی نامعتبر خطای اعتبارسنجی ساخت‌یافته ایجاد می‌کند. استریم نشست از اعتبارسنجی ساخت‌یافته پشتیبانی نمی‌کند.

## استریم و استفاده ناهمگام

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

برای استفاده ناهمگام، `ask_async()` و `ask_stream_async()` را با `await` و `async for` به کار ببرید. رویدادهای استریم تایپ‌شده شامل `TextDelta`، `UsageUpdate`، `Completed` و `Error` هستند. نوع `ToolCall` export شده است، اما adapterهای فعلی ارائه‌دهندگان رویداد فراخوانی ابزار تولید نمی‌کنند. برای دریافت رویدادها از `ask_stream_events()` یا `ask_stream_events_async()` استفاده کنید. لغو عملیات و خطاهای ارائه‌دهنده را در برنامه خود مدیریت کنید.

## تولید رسانه و دانلود امن

برخی ارائه‌دهندگان با `output_type="image"` یا `"audio"` رسانه تولید می‌کنند؛ دسترسی به این قابلیت به ارائه‌دهنده و مدل بستگی دارد. API درخواست فعلی ورودی تصویر برای vision نمی‌پذیرد.

دانلود امن رسانه به extra `httpx` نیاز دارد. به‌طور پیش‌فرض HTTPS الزامی است، redirect و پاسخ DNS غیرعمومی رد می‌شوند، محدودیت ۲۵ MiB و ۳۰ ثانیه اعمال می‌شود. می‌توان MIME type و host را محدود کرد.

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

`allow_private=True` را فقط برای میزبان خصوصی مورداعتماد فعال کنید. سیاست دانلود به‌تنهایی هر URL تولیدشده توسط ارائه‌دهنده را برای استفاده‌های دیگر امن نمی‌کند.

## نشست‌ها و چرخه عمر کلاینت

`provider.session()` یک گفت‌وگوی اختیاری در حافظه ایجاد می‌کند:

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

تاریخچه در حافظه فرایند است و ذخیره دائمی نمی‌شود. `max_messages` تاریخچه را بر اساس زوج پیام کاربر/دستیار محدود می‌کند. فراخوانی‌های همگام هم‌زمان با هم و فراخوانی‌های ناهمگام نیز با هم سری می‌شوند؛ این دو نوع عملیات را هم‌زمان در یک نشست ترکیب نکنید.

ارائه‌دهندگان از `close()`/`aclose()` و context managerهای همگام/ناهمگام پشتیبانی می‌کنند. پس از پایان کار کلاینت را ببندید. کلاینت async ذخیره‌شده به نخستین event loop مورد استفاده وابسته است؛ برای هر loop یک نمونه ارائه‌دهنده بسازید.

## قابلیت‌ها و مشاهده‌پذیری

قابلیت‌های اعلام‌شده را با `provider.capabilities()` بررسی کنید. با `provider.use(Observability(...))` یک hook مشاهده‌پذیری اضافه کنید تا اطلاعات ارائه‌دهنده، مدل، تأخیر، تعداد تلاش‌ها و مصرف نرمال‌شده توکن را دریافت کنید. هزینه تخمینی تنها با ارائه نرخ قیمت و گزارش مصرف از سوی ارائه‌دهنده محاسبه می‌شود.

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

اطلاعات محرمانه یا prompt حساس را به handlerهای telemetry خود ارسال نکنید. خطای hook درخواست را متوقف نمی‌کند.

## معماری

`ask_ai` شامل کلاس پایه مشترک ارائه‌دهنده، adapterهای SDK، `Response` یکپارچه، `Router` و `ConversationSession` اختیاری و ابزارهای خروجی ساخت‌یافته و امنیت رسانه است. SDKها به‌صورت اختیاری import می‌شوند، بنابراین برای import بسته نیازی به نصب همه یکپارچه‌سازی‌ها نیست. درخواست‌ها از سرویس متعلق به کتابخانه عبور نمی‌کنند.

## رابط خط فرمان

فرمان `ask-ai` پس از نصب در دسترس است و از OpenAI، Groq، Google، OpenRouter، Azure و Anthropic پشتیبانی می‌کند:

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

CLI از اعتبارنامه محیطی ارائه‌دهنده انتخاب‌شده استفاده می‌کند. ارائه‌دهنده عمومی سازگار با OpenAI در Python API موجود است، اما در گزینه‌های فعلی CLI نیست.

## سازگاری و عیب‌یابی

- **پایتون:** classifierهای بسته نسخه‌های 3.10 تا 3.13 را فهرست می‌کنند؛ حداقل نسخه 3.10 است.
- **تایپینگ:** بسته `ask_ai/py.typed` را دارد.
- **SDK نصب نیست:** extra مربوط، مانند `askai-python[openai]`، را نصب کنید.
- **اعتبارنامه موجود نیست:** متغیر محیطی بالا را تنظیم یا `api_key=` را ارسال کنید.
- **خطای راه‌اندازی Azure:** endpoint، کلید و deployment/model را تنظیم کنید.
- **گزینه ناشناخته:** املا را بررسی کنید یا `strict_options=True` را فعال کنید.
- **خطای event loop:** کلاینت async را بین event loopها مشترک نکنید.
- **خروجی ساخت‌یافته نامعتبر:** مدل/Schema را بررسی کنید؛ تلاش اضافه می‌تواند هزینه‌زا باشد.
- **رفتار API زنده:** تست‌های mock پذیرش مدل/گزینه در API زنده را تضمین نمی‌کنند؛ آزمون یکپارچه‌سازی واقعی ممکن است هزینه داشته باشد.

## مشارکت، پشتیبانی و مجوز

گزارش خطا و پیشنهاد قابلیت را در [issue tracker](https://github.com/Hosseinghorbani0/ask-ai/issues) ثبت کنید. مشارکت کد باید تست مرتبط و در صورت تغییر رفتار، به‌روزرسانی مستندات داشته باشد. پیش از ارسال `python -m pytest -q` و `ruff check .` را اجرا کنید. تاریخچه نسخه‌ها در [CHANGELOG.md](../CHANGELOG.md) است.

پروژه با [مجوز MIT](../LICENSE) منتشر می‌شود. برای درخواست پشتیبانی یک نمونه بازتولید حداقلی ارائه دهید و کلید API، اطلاعات شخصی و سایر اسرار را حذف کنید. صفحه [PyPI](https://pypi.org/project/askai-python/) و [مخزن GitHub](https://github.com/Hosseinghorbani0/ask-ai) را نیز ببینید.
