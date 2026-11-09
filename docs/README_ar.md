# ask-ai

[![إصدار PyPI](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![إصدارات Python](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![ترخيص MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**حزمة Python صغيرة ومُعرّفة الأنواع لاستدعاء عدة مزوّدي LLM من خلال واجهة API موحّدة.**
استخدمها في البرامج النصية وتطبيقات Python من دون اعتماد إطار عمل تنسيق كبير.

`ask-ai` مكتبة عميل، وليست خدمة مستضافة أو بوابة. أنشئ عميل مزوّد، واستدعِه تزامنيًا أو غير تزامني، واحصل على كائن `Response` موحّد. حزم SDK للمزوّدين اختيارية؛ ثبّت ما تحتاج إليه فقط.

## لغات الوثائق

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## المحتويات

- [الميزات](#الميزات)
- [المتطلبات والتثبيت](#المتطلبات-والتثبيت)
- [المزوّدون](#المزودون)
- [البدء السريع](#البدء-السريع)
- [واجهة API العامة](#واجهة-api-العامة)
- [خيارات الطلب](#خيارات-الطلب)
- [إعادة المحاولة والبدائل والتوجيه](#إعادة-المحاولة-والبدائل-والتوجيه)
- [المخرجات المنظّمة](#المخرجات-المنظمة)
- [البث والاستخدام غير المتزامن](#البث-والاستخدام-غير-المتزامن)
- [إنشاء الوسائط والتنزيل الآمن](#إنشاء-الوسائط-والتنزيل-الآمن)
- [الجلسات ودورة حياة العميل](#الجلسات-ودورة-حياة-العميل)
- [القدرات وقابلية المراقبة](#القدرات-وقابلية-المراقبة)
- [البنية](#البنية)
- [واجهة سطر الأوامر](#واجهة-سطر-الأوامر)
- [التوافق واستكشاف الأخطاء](#التوافق-واستكشاف-الأخطاء)
- [المساهمة والدعم والترخيص](#المساهمة-والدعم-والترخيص)

## الميزات

- واجهات موحّدة: `ask` و`ask_async` و`ask_stream` و`ask_stream_async`.
- الانتقال الاحتياطي بين المزوّدين والتوجيه وفق السياسات.
- إعادة المحاولة عند الأعطال العابرة، مع مهلة للطلب الواحد وأخرى للعملية كاملة.
- بيانات استجابة وصفية محددة الأنواع، واستخدام موحّد للرموز، وخطافات مراقبة اختيارية.
- JSON ومخرجات منظّمة يجري التحقق منها لدى المزوّدين المدعومين.
- جلسات محادثة اختيارية في الذاكرة.
- نقاط نهاية متوافقة مع OpenAI Chat Completions، بما فيها الخوادم المحلية.
- تنزيل آمن للوسائط تتحكم به السياسات.

ترسل واجهة الطلب العامة النص حاليًا؛ ولا تعني بيانات القدرات أن إدخال الصور للرؤية مدعوم. لا تتوفر آلية تنفيذ استدعاءات الأدوات أو تخزين دائم للمحادثات.

## المتطلبات والتثبيت

- Python 3.10 أو أحدث.
- لا يتطلب الإصدار الأساسي أي اعتماديات. حزم SDK للمزوّدين ومكتبات الوسائط والمخرجات المنظّمة إضافات اختيارية.

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI وAzure OpenAI وOpenRouter والنقاط المتوافقة
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic وjsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # التنزيل الآمن للوسائط
python -m pip install "askai-python[all]"
```

ضع بيانات الاعتماد في متغيرات البيئة أو مرّر `api_key=` عند إنشاء المزوّد. لا تضع الأسرار في الشيفرة المصدرية.

## المزوّدون

| المزوّد | الاستيراد | الإضافة | متغير البيئة | النموذج الافتراضي |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | يلزم تحديد deployment |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| متوافق مع OpenAI | `OpenAICompatibleProvider` | `openai` | لا يوجد (اختياري) | مطلوب عند الإنشاء |

يتطلب Azure أيضًا `AZURE_OPENAI_ENDPOINT`. يمكن تمرير deployment عبر `model=` أو `AZURE_OPENAI_DEPLOYMENT_NAME`. القيمة الافتراضية لـ `AZURE_OPENAI_API_VERSION` هي `2024-06-01`. يحتاج المزوّد المتوافق إلى `base_url` مطلق من HTTP(S) ونموذج؛ ويمكن حذف `api_key` عند استخدام نقطة نهاية محلية.

تعرض `capabilities()` الدعم المعلن للنص والبث والبث غير المتزامن والمخرجات المنظّمة واستدعاءات الأدوات وإنشاء الصور/الصوت والرؤية. لا يضمن ذلك توافر الميزة لنموذج أو حساب معين. تنفيذ الأدوات وإدخال الصور للرؤية ليسا ميزتين عامتين للطلبات.

## البدء السريع

```python
from ask_ai import OpenAI

client = OpenAI()  # يقرأ OPENAI_API_KEY
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## واجهة API العامة

| الطريقة | النتيجة | الوصف |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | طلب تزامني |
| `await provider.ask_async(query, **options)` | `Response` | طلب غير متزامن أصلي |
| `provider.ask_stream(query, **options)` | مكرّر نصوص | بث نصي تزامني |
| `async for chunk in provider.ask_stream_async(...)` | مكرّر غير متزامن | بث نصي غير متزامن |
| `provider.ask_stream_events(...)` | مكرّر أحداث | بث تزامني محدد الأنواع |
| `provider.ask_stream_events_async(...)` | مكرّر أحداث غير متزامن | بث غير متزامن محدد الأنواع |

يوفر `Response` الخصائص `text` و`raw` الأصلي و`json` المحلّل و`parsed`/`pydantic` عند تحديد `response_model`، إلى جانب `media` و`usage` و`metadata` الاختيارية. تحلّل `response.json` نص الاستجابة؛ استخدم `json=True` لطلب تنسيق JSON أو `response_model=...` للتحقق.

## خيارات الطلب

مرّر الخيارات في الطلب أو عيّن القيم الافتراضية عبر `provider.advanced(...)`؛ وتكون خيارات الطلب ذات أولوية.

| الخيار | الغرض |
|---|---|
| `temperature` و`max_tokens` و`top_p` | عناصر التحكم الشائعة في التوليد |
| `frequency_penalty` و`presence_penalty` و`stop` | إعدادات يدعمها المزوّد |
| `system_message` (الاسمان البديلان `system` و`prompt`) | تعليمات النظام |
| `timeout` | مهلة استدعاء المزوّد الواحد (30 ثانية افتراضيًا في العملاء) |
| `total_timeout` | مهلة العملية الكاملة بما فيها المحاولات |
| `retry` | عدد المحاولات الإضافية؛ الافتراضي 2 (حتى 3 محاولات) |
| `json=True` | طلب إخراج JSON وإتاحة تحليله عبر `response.json` |
| `response_model` و`validation_retries` | تحليل نموذج منظّم مدعوم والتحقق منه |
| `output_type` | طلب إخراج `image` أو `audio` مدعوم |
| `clean` و`strip` و`code` | تنظيف النص أو استخراجه عند قراءة `response.text` |
| `strict_options=True` | إصدار خطأ عند الخيار المجهول بدلًا من التحذير |

يختلف الدعم باختلاف المزوّد والنموذج. تُصدر الخيارات غير المعروفة تحذيرًا افتراضيًا، ويؤدي الوضع الصارم إلى `ValueError`. الخيار المهمل `safe_mode` ليس له سلوك محدد. تؤدي أنواع الإخراج غير المدعومة إلى خطأ صريح.

## إعادة المحاولة والبدائل والتوجيه

تُعاد المحاولة افتراضيًا مرتين عند الأعطال العابرة القابلة لإعادة المحاولة (حتى ثلاث محاولات). لا تُعاد أخطاء الطلبات غير الصالحة أو المصادقة. يُحترم `Retry-After` بحد أقصى 30 ثانية. يقيّد `timeout` استدعاءً واحدًا، بينما يقيّد `total_timeout` العملية كاملة.

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

لا ينتقل التسلسل إلى المزوّد التالي إلا عند خطأ قابل لإعادة المحاولة. يوفّر `Router` اختيارًا قائمًا على السياسات وميزانية إجمالية عبر `max_attempts`. قد تؤدي المحاولات الإضافية إلى تكلفة إضافية. لا يعاد تشغيل البث بعد إصدار أجزاء منه.

## المخرجات المنظّمة

تُدعم نماذج Pydantic وdataclasses و`TypedDict` ومخططات JSON. تكون النتيجة كائن `Response` عاديًا، ويمكن الوصول إلى القيمة المتحقق منها عبر `.parsed`.

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

يختلف دعم المخططات الأصلي بين المزوّدين، ويجري التحقق محليًا. تؤدي المخرجات غير الصالحة إلى خطأ تحقق منظّم. لا يدعم بث الجلسة التحقق المنظّم.

## البث والاستخدام غير المتزامن

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

للاستخدام غير المتزامن، استخدم `ask_async()` و`ask_stream_async()` مع `await` و`async for`. تشمل أحداث البث المحددة الأنواع `TextDelta` و`UsageUpdate` و`Completed` و`Error`. النوع `ToolCall` متاح للتصدير، لكن محوّلات المزوّدين الحالية لا تصدر أحداث استدعاء أدوات. استخدم `ask_stream_events()` أو `ask_stream_events_async()` لاستقبال الأحداث. عالج الإلغاء وأخطاء المزوّد في تطبيقك.

## إنشاء الوسائط والتنزيل الآمن

تنفّذ بعض المزوّدات إنشاء الصور أو الصوت عبر `output_type="image"` أو `"audio"`؛ ويعتمد ذلك على المزوّد والنموذج. لا تقبل واجهة الطلب الحالية صورًا كمدخل للرؤية.

يتطلب تنزيل الوسائط الآمن إضافة `httpx`. افتراضيًا، يُشترط HTTPS وتُرفض عمليات إعادة التوجيه وعناوين DNS غير العامة، ويُطبّق حد 25 MiB ومهلة 30 ثانية. يمكن تقييد أنواع MIME والمضيفين.

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

لا تستخدم `allow_private=True` إلا مع عناوين الشبكات الخاصة الموثوقة. لا تجعل سياسة التنزيل كل URL ينشئه المزوّد آمنًا للاستخدامات الأخرى.

## الجلسات ودورة حياة العميل

ينشئ `provider.session()` محادثة اختيارية في الذاكرة:

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

يُحفظ السجل في ذاكرة العملية ولا يستمر بعد انتهائها. يحد `max_messages` السجل بحسب أزواج رسائل المستخدم/المساعد. تُسلسل الطلبات التزامنية المتزامنة فيما بينها، وكذلك الطلبات غير المتزامنة؛ لا تخلط العمليتين بالتزامن في الجلسة نفسها.

تدعم المزوّدات `close()`/`aclose()` ومديري السياق التزامني وغير التزامني. أغلق العملاء عند الانتهاء. يرتبط العميل غير المتزامن المخزّن مؤقتًا بأول event loop يستخدمه؛ أنشئ مزوّدًا لكل loop.

## القدرات وقابلية المراقبة

استخدم `provider.capabilities()` لمعرفة الدعم المعلن. أرفق خطاف المراقبة عبر `provider.use(Observability(...))` لاستقبال بيانات المزوّد والنموذج والكمون وعدد المحاولات واستخدام الرموز الموحّد. لا يُقدّر السعر إلا عند تزويد الأسعار وإبلاغ المزوّد عن الاستهلاك.

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

لا ترسل المطالبات الحساسة أو بيانات الاعتماد إلى معالجات القياس عن بُعد الخاصة بك. لا تؤدي أخطاء الخطاف إلى تعطيل الطلب.

## البنية

تتكون `ask_ai` من فئة أساس مشتركة للمزوّدين، ومحوّلات SDK خاصة بكل مزوّد، و`Response` موحّد، و`Router` و`ConversationSession` اختياريين، وأدوات للمخرجات المنظّمة وأمان الوسائط. تُستورد SDK اختياريًا، لذلك لا يلزم تثبيت كل عمليات التكامل لاستيراد الحزمة. لا تمر الطلبات عبر خدمة تابعة للمكتبة.

## واجهة سطر الأوامر

يوفر التثبيت الأمر `ask-ai`، ويدعم OpenAI وGroq وGoogle وOpenRouter وAzure وAnthropic:

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

يستخدم CLI بيانات اعتماد المزوّد المختار في البيئة. يتوفر المزوّد العام المتوافق مع OpenAI عبر Python API، وليس ضمن خيارات CLI الحالية.

## التوافق واستكشاف الأخطاء

- **Python:** تذكر مصنّفات الحزمة الإصدارات 3.10–3.13؛ والحد الأدنى المعلن 3.10.
- **الأنواع:** تتضمن الحزمة `ask_ai/py.typed`.
- **SDK غير مثبتة:** ثبّت الإضافة المناسبة، مثل `askai-python[openai]`.
- **بيانات اعتماد مفقودة:** عيّن متغير البيئة المناسب أو مرّر `api_key=`.
- **فشل تهيئة Azure:** عيّن endpoint والمفتاح وdeployment/model.
- **خيار غير معروف:** تحقق من تهجئته أو استخدم `strict_options=True`.
- **خطأ event loop:** لا تعِد استخدام عميل غير متزامن بين حلقات أحداث مختلفة.
- **مخرجات منظّمة غير صالحة:** تحقق من النموذج/المخطط؛ قد تؤدي المحاولات الإضافية إلى رسوم.
- **سلوك API الحقيقي:** لا تضمن اختبارات mock قبول API الحي لنموذج أو خيار؛ وقد تترتب رسوم على الاختبارات الحية.

## المساهمة والدعم والترخيص

أرسل تقارير الأخطاء وطلبات الميزات عبر [متتبع المشكلات](https://github.com/Hosseinghorbani0/ask-ai/issues). ينبغي أن تتضمن مساهمات الشيفرة اختبارات محددة وتحديث الوثائق عند تغيير السلوك. شغّل `python -m pytest -q` و`ruff check .` قبل الإرسال؛ راجع [CHANGELOG.md](../CHANGELOG.md).

المشروع مرخّص بموجب [MIT](../LICENSE). أرفق مثالًا صغيرًا قابلًا لإعادة الإنتاج مع طلبات الدعم، واحذف مفاتيح API والبيانات الشخصية والأسرار الأخرى. راجع أيضًا [PyPI](https://pypi.org/project/askai-python/) و[مستودع GitHub](https://github.com/Hosseinghorbani0/ask-ai).
