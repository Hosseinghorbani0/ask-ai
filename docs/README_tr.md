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
  <b>Sadece tek bir satır kodla LLM sağlayıcıları arasında geçiş yapmak için minimal bir Python SDK'sı.</b><br/>
  Ekstra framework yok. Sunucuya gerek yok. Karmaşıklık yok.
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Hızlı Başlangıç (5 Saniye)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# Çevreden otomatik olarak OPENAI_API_KEY algılar
OpenAI().ask("Kara delikleri 5 yaşındaki bir çocuğa anlatır gibi açıkla").text

# Sağlayıcıları anında değiştirin
Groq().ask("Kara delikleri 5 yaşındaki bir çocuğa anlatır gibi açıkla").text
```

---

## 🧐 Neden ask-ai?

- **Tek bir fonksiyon**: Sadece `.ask()` çağrısı yapın.
- **Birden çok sağlayıcı**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **Sıfır yapılandırma**: Anahtarlar otomatik olarak ortam değişkenlerinden çekilir.
- **Öncelik SDK, Framework değil**: Sisteminize veya mimarinize müdahale etmez.

## 🚫 Bu proje ne DEĞİLDİR

> ❌ Büyük bir AI framework'ü değildir.
> ❌ Bir API Gateway değildir.
> ❌ Sistem hafızasını yöneten bir Agent değildir.

Bu proje sadece tek bir şeyi mükemmel yapar: **LLM'lere yapılan API çağrılarını basitleştirmek.**

---

## 🛠️ Gelişmiş Kullanım

### 🧰 Geliştirici Araçları (Auto-Parsing)
Model çıktılarını temizlemek için Regex yazmayı bırakın! `ask-ai` yerleşik metin işleme işaretleriyle (flags) gelir:

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (```json gibi etiketleri temizler)
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (Sadece kod bloğunu çıkarır, sohbeti yok sayar)
code = ai.ask("Write a python script", code=True).text

# 3. Strip Tags (<think> ve HTML etiketlerini kaldırır)
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (Doğrudan işlenmiş bir Python Sözlüğü döndürür)
data_dict = ai.ask("Extract info", json=True).json
print(data_dict['name'])
```

### 🔄 Yerleşik Yeniden Deneme ve Zaman Aşımı (Resiliency)
Hız sınırlarını (`429`) ve ağ kesintilerini otomatik olarak yönetin:

```python
# Ağ hatası durumunda 3 defaya kadar tekrar dener, genel zaman aşımı 10 saniye
response = ai.ask("Bir python scripti yaz", retry=3, timeout=10)
```

### ⚙ Sistem Yapılandırması 
Sistem rollerini ve temperature değerini doğrudan ayarlayın:

```python
ai.advanced(
    temperature=0.7,
    prompt="Sen kıdemli bir DevOps mühendisisin."
)

print(ai.ask("Bir Dockerfile'ı nasıl optimize ederim?").text)
```

---

## 🔗 Önemli Bağlantılar

- **GitHub Deposu**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (Bize bir yıldız vermeyi unutmayın! ⭐)
- **PyPI Paketi**: [askai-python](https://pypi.org/project/askai-python/)
- **Resmi Web Sitesi**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
