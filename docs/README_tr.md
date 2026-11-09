# ask-ai

[![PyPI sürümü](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Python sürümleri](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![MIT Lisansı](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**Birden fazla LLM sağlayıcısını tutarlı bir API üzerinden çağırmak için küçük ve tipli bir Python SDK'sı.**
Büyük bir orkestrasyon çatısı benimsemeden betiklerde ve Python uygulamalarında kullanın.

`ask-ai` barındırılan bir servis veya ağ geçidi değil, istemci kütüphanesidir. Bir sağlayıcı istemcisi oluşturup eşzamanlı ya da eşzamansız çağrı yaparsınız ve ortak bir `Response` nesnesi alırsınız. Sağlayıcı SDK'ları isteğe bağlıdır; yalnızca kullandıklarınızı kurun.

## Dokümantasyon dilleri

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## İçindekiler

- [Özellikler](#özellikler)
- [Gereksinimler ve kurulum](#gereksinimler-ve-kurulum)
- [Sağlayıcılar](#sağlayıcılar)
- [Hızlı başlangıç](#hızlı-başlangıç)
- [Genel API](#genel-api)
- [İstek seçenekleri](#istek-seçenekleri)
- [Yeniden deneme, yedek sağlayıcı ve yönlendirme](#yeniden-deneme-yedek-sağlayıcı-ve-yönlendirme)
- [Yapılandırılmış çıktı](#yapılandırılmış-çıktı)
- [Akış ve eşzamansız kullanım](#akış-ve-eşzamansız-kullanım)
- [Medya üretimi ve güvenli indirme](#medya-üretimi-ve-güvenli-indirme)
- [Oturumlar ve istemci yaşam döngüsü](#oturumlar-ve-istemci-yaşam-döngüsü)
- [Yetenekler ve gözlemlenebilirlik](#yetenekler-ve-gözlemlenebilirlik)
- [Mimari](#mimari)
- [Komut satırı](#komut-satırı)
- [Uyumluluk ve sorun giderme](#uyumluluk-ve-sorun-giderme)
- [Katkı, destek ve lisans](#katkı-destek-ve-lisans)

## Özellikler

- Tutarlı `ask`, `ask_async`, `ask_stream` ve `ask_stream_async` API'leri.
- Sağlayıcı geri dönüşü ve politika tabanlı yönlendirme.
- Geçici hatalar için yeniden deneme; çağrı ve toplam süre sınırları.
- Tipli yanıt meta verileri, normalleştirilmiş token kullanımı ve isteğe bağlı gözlemlenebilirlik kancaları.
- Desteklenen sağlayıcılarda JSON ve doğrulanan yapılandırılmış yanıtlar.
- İsteğe bağlı, bellek içi konuşma oturumları.
- Yerel sunucular dahil OpenAI Chat Completions uyumlu uç noktalar.
- Politikalarla denetlenen güvenli medya indirmeleri.

Genel istek API'si şu anda metin gönderir; yetenek bilgileri görüntü girdisiyle vision desteğini garanti etmez. Araç çağrılarının yürütülmesi ve kalıcı konuşma saklama sunulmaz.

## Gereksinimler ve kurulum

- Python 3.10 veya üzeri.
- Temel paketin zorunlu bağımlılığı yoktur. Sağlayıcı SDK'ları ile medya/yapılandırılmış çıktı kütüphaneleri isteğe bağlı eklerdir.

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI, Azure OpenAI, OpenRouter ve uyumlu uç noktalar
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic ve jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # güvenli medya indirme
python -m pip install "askai-python[all]"
```

Kimlik bilgilerini ortam değişkeninde tutun veya sağlayıcı oluştururken `api_key=` ile verin. Gizli bilgileri kaynak koduna koymayın.

## Sağlayıcılar

| Sağlayıcı | İçe aktarma | Ek | Ortam değişkeni | Varsayılan model |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | Deployment adı gerekli |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| OpenAI uyumlu | `OpenAICompatibleProvider` | `openai` | Yok (isteğe bağlı) | Oluştururken gerekli |

Azure ayrıca `AZURE_OPENAI_ENDPOINT` gerektirir. Deployment `model=` ile veya `AZURE_OPENAI_DEPLOYMENT_NAME` üzerinden verilebilir. `AZURE_OPENAI_API_VERSION` varsayılanı `2024-06-01` değeridir. Uyumlu sağlayıcı mutlak HTTP(S) `base_url` ve model gerektirir; yerel uç noktalarda `api_key` atlanabilir.

`capabilities()` metin, akış, eşzamansız akış, yapılandırılmış çıktı, araç çağrıları, görüntü/ses üretimi ve vision için beyan edilen desteği döndürür. Belirli bir model veya hesapta özelliğin kullanılacağını garanti etmez. Araç çağrısı yürütme ve vision girdisi genel istek özellikleri olarak sunulmaz.

## Hızlı başlangıç

```python
from ask_ai import OpenAI

client = OpenAI()  # OPENAI_API_KEY ortam değişkenini okur
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## Genel API

| Metot | Sonuç | Açıklama |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | Eşzamanlı istek |
| `await provider.ask_async(query, **options)` | `Response` | Yerel eşzamansız istek |
| `provider.ask_stream(query, **options)` | Metin yineleyicisi | Eşzamanlı metin akışı |
| `async for chunk in provider.ask_stream_async(...)` | Eşzamansız yineleyici | Eşzamansız metin akışı |
| `provider.ask_stream_events(...)` | Olay yineleyicisi | Tipli eşzamanlı akış |
| `provider.ask_stream_events_async(...)` | Eşzamansız olay yineleyicisi | Tipli eşzamansız akış |

`Response`; `text`, değiştirilmemiş `raw`, ayrıştırılmış `json`, `response_model` istendiyse `parsed`/`pydantic`, ayrıca isteğe bağlı `media`, `usage` ve `metadata` sağlar. `response.json` yanıt metnini ayrıştırır. JSON biçimi istemek için `json=True`, doğrulama için `response_model=...` kullanın.

## İstek seçenekleri

Seçenekleri isteğe ekleyin veya `provider.advanced(...)` ile varsayılanları belirleyin; istek seçenekleri önceliklidir.

| Seçenek | Amaç |
|---|---|
| `temperature`, `max_tokens`, `top_p` | Yaygın üretim denetimleri |
| `frequency_penalty`, `presence_penalty`, `stop` | Sağlayıcının desteklediği üretim denetimleri |
| `system_message` (diğer adları: `system`, `prompt`) | Sistem talimatı |
| `timeout` | Tek sağlayıcı çağrısının sınırı (istemcilerde varsayılan 30 saniye) |
| `total_timeout` | Yeniden denemeler dahil tüm işlem için süre sınırı |
| `retry` | Ek deneme sayısı; varsayılan 2 (en fazla 3 deneme) |
| `json=True` | JSON biçimi ister ve `response.json` ayrıştırmasını sağlar |
| `response_model`, `validation_retries` | Desteklenen yapılandırılmış modeli ayrıştırır/doğrular |
| `output_type` | Desteklenen `image` veya `audio` çıktısını ister |
| `clean`, `strip`, `code` | `response.text` okunurken metni temizler/çıkarır |
| `strict_options=True` | Bilinmeyen seçeneklerde uyarı yerine hata verir |

Seçenek desteği sağlayıcıya ve modele göre değişir. Bilinmeyen seçenekler varsayılan olarak uyarı verir; katı kipte `ValueError` oluşur. Kullanımdan kaldırılan `safe_mode` tanımlı davranışa sahip değildir. Desteklenmeyen çıktı türleri açıkça hata verir.

## Yeniden deneme, yedek sağlayıcı ve yönlendirme

Yeniden denenebilir geçici hatalarda varsayılan olarak iki ek deneme yapılır (toplam üç denemeye kadar). Geçersiz istek ve kimlik doğrulama hataları yeniden denenmez. `Retry-After` en fazla 30 saniye olacak şekilde uygulanır. `timeout` tek çağrıyı, `total_timeout` tüm işlemi sınırlar.

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

Yedek sağlayıcıya yalnızca yeniden denenebilir sağlayıcı hatalarında geçilir. `Router`, politika tabanlı seçim ve genel `max_attempts` sınırı sunar. Yeniden deneme ek maliyet getirebilir. Akış parçası gönderildikten sonra akış yeniden denenmez.

## Yapılandırılmış çıktı

Pydantic modelleri, dataclass, `TypedDict` ve JSON Schema desteklenir. Doğrulanan sonucu `Response` nesnesinin `.parsed` özelliğinden alın.

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

Yerel doğrulama yapılır ve sağlayıcının yerel şema desteği değişebilir. Geçersiz çıktı yapılandırılmış doğrulama hatası verir. Oturum akışlarında yapılandırılmış doğrulama desteklenmez.

## Akış ve eşzamansız kullanım

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

Eşzamansız istekler için `ask_async()` ve `ask_stream_async()` metotlarını `await` / `async for` ile kullanın. Mevcut tipli akış olayları `TextDelta`, `UsageUpdate`, `Completed` ve `Error` içerir. `ToolCall` bir olay türü olarak dışa aktarılır, ancak mevcut sağlayıcı adaptörleri araç çağrısı olayı üretmez. Olaylar için `ask_stream_events()` veya `ask_stream_events_async()` kullanın. İptal ve sağlayıcı hatalarını uygulamanızda ele alın.

## Medya üretimi ve güvenli indirme

Bazı sağlayıcılar `output_type="image"` veya `"audio"` ile medya üretir; kullanılabilirlik sağlayıcıya ve modele bağlıdır. İstek API'si şu anda vision için görüntü girdisi almaz.

Güvenli medya indirmeleri `httpx` ekini gerektirir. Varsayılan olarak HTTPS zorunludur, yönlendirmeler ve genel olmayan DNS yanıtları reddedilir; 25 MiB ve 30 saniye sınırı uygulanır. MIME türleri ve ana makineler kısıtlanabilir.

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

`allow_private=True` seçeneğini yalnızca güvenilir özel ağ URL'lerinde kullanın. İndirme politikası, sağlayıcıların oluşturduğu her URL'yi başka kullanım amaçları için güvenli hale getirmez.

## Oturumlar ve istemci yaşam döngüsü

`provider.session()` isteğe bağlı, bellek içi konuşma durumu oluşturur:

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

Geçmiş işlem belleğinde tutulur ve kalıcı değildir. `max_messages` kullanıcı/asistan çiftleri üzerinden sınırlar. Eşzamanlı sync çağrılar kendi aralarında, async çağrılar da kendi aralarında serileştirilir; aynı oturumda sync ve async işlemleri eşzamanlı karıştırmayın.

Sağlayıcılar `close()`/`aclose()` ve eşzamanlı/eşzamansız bağlam yöneticilerini destekler. İşiniz bittiğinde istemcileri kapatın. Önbelleğe alınmış async istemci ilk kullanıldığı event loop'a bağlıdır; her loop için ayrı sağlayıcı oluşturun.

## Yetenekler ve gözlemlenebilirlik

Beyan edilen desteği `provider.capabilities()` ile inceleyin. `provider.use(Observability(...))` ile gözlemlenebilirlik kancası ekleyerek sağlayıcı, model, gecikme, deneme sayısı ve normalleştirilmiş token kullanımı bilgilerini alın. Tahmini maliyet yalnızca fiyatlandırma ve sağlayıcı kullanım bilgisi varsa hesaplanır.

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

Kendi telemetri işleyicilerinize gizli bilgileri veya hassas istemleri eklemeyin. Hook hataları isteği kesmez.

## Mimari

`ask_ai`, ortak sağlayıcı temelini, sağlayıcıya özel SDK adaptörlerini, ortak `Response` nesnesini, isteğe bağlı `Router` ve `ConversationSession` bileşenlerini ve yapılandırılmış çıktı/medya güvenliği yardımcılarını içerir. SDK'lar isteğe bağlı içe aktarıldığından tüm entegrasyonları kurmadan paket içe aktarılabilir. İstekler kütüphanenin kendi hizmetinden geçmez.

## Komut satırı

Kurulum `ask-ai` komutunu sağlar. OpenAI, Groq, Google, OpenRouter, Azure ve Anthropic desteklenir:

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

CLI, seçilen sağlayıcının ortam değişkeni kimlik bilgilerini kullanır. Genel OpenAI uyumlu sağlayıcı Python API'sinde kullanılabilir; mevcut CLI seçeneklerinde yoktur.

## Uyumluluk ve sorun giderme

- **Python:** Paket sınıflandırıcıları 3.10–3.13'ü listeler; belirtilen minimum 3.10'dur.
- **Tip bilgisi:** Dağıtım `ask_ai/py.typed` içerir.
- **SDK bulunamadı:** İlgili eki, örneğin `askai-python[openai]`, kurun.
- **Kimlik bilgisi eksik:** Belirtilen ortam değişkenini ayarlayın veya `api_key=` verin.
- **Azure başlatma hatası:** endpoint, anahtar ve deployment/model değerlerini ayarlayın.
- **Bilinmeyen seçenek:** Yazımı kontrol edin veya `strict_options=True` kullanın.
- **Event loop hatası:** Async istemciyi farklı event loop'larda yeniden kullanmayın.
- **Yapılandırılmış çıktı geçersiz:** Modeli/şemayı kontrol edin; ek denemelerin ücret doğurabileceğini unutmayın.
- **Canlı API:** Sahte sağlayıcı testleri canlı sağlayıcı davranışını garanti etmez; gerçek entegrasyon testleri ücretli olabilir.

## Katkı, destek ve lisans

Hata ve özellik istekleri için [issue takip sistemini](https://github.com/Hosseinghorbani0/ask-ai/issues) kullanın. Kod katkılarına hedefli testler ve davranış değişiklikleri için dokümantasyon güncellemeleri ekleyin. Göndermeden önce `python -m pytest -q` ve `ruff check .` çalıştırın; sürüm geçmişi [CHANGELOG.md](../CHANGELOG.md) içindedir.

Proje [MIT Lisansı](../LICENSE) ile dağıtılır. Destek başvurularına en küçük yeniden üretilebilir örneği ekleyin ve API anahtarlarını, kişisel verileri ve diğer gizli bilgileri çıkarın. Ayrıca [PyPI](https://pypi.org/project/askai-python/) ve [GitHub deposuna](https://github.com/Hosseinghorbani0/ask-ai) bakın.
