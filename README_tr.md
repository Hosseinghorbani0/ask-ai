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

**Yapay Zeka Basitleştirildi.**
OpenAI, Groq, Google, Anthropic ve daha fazlasına tek bir kod satırıyla bağlanın.

> Her sağlayıcı için yapay zeka kodunu yeniden yazmayı bırakın. Tek satır kullanın. Modeller arasında istediğiniz zaman geçiş yapın.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ Neden easyai?

- **SDK Kilidi Yok**: 5 farklı kütüphane öğrenmeyin. Bir tane öğrenin.
- **Birleşik API**: `ai.ask()` tüm sağlayıcılarda metin, görüntü ve ses için çalışır.
- **Üretime Hazır**: Yerleşik tip güvenliği, hata yönetimi ve ortam yönetimi.
- **Sıfır Yapılandırma**: API anahtarlarını ortamınızdan otomatik olarak algılar.

---

## 🚀 Altın Örnek (The Golden Example)

`easyai`nin gücünü 3 satır kodda görün:

```python
from easyai import OpenAI, Anthropic, Google

prompt = "Kuantum hesaplamayı tek bir cümlede açıkla."

# Sağlayıcıları anında değiştirin
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 Kurulum

```bash
pip install easyai
```

---

## 📖 Hızlı Başlangıç Rehberi

### 1. Kurulum
API anahtarlarınızı dışa aktarın (veya açıkça iletin).
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Standart Kullanım
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("Merhaba Dünya!"))
```

### 3. Gelişmiş Kullanım (Profesyonel)
Profesyonel sonuçlar için `temperature`, `top_p` ve sistem personalarını (`prompt`) kontrol edin.

```python
ai.advanced(
    temperature=0.7,
    prompt="Sen kıdemli bir DevOps mühendisisin."
)

print(ai.ask("Bir Dockerfile'ı nasıl optimize ederim?"))
```

---

## 🔌 Desteklenen Sağlayıcılar

| Sağlayıcı | Sınıf | Özellik Seti |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | Tüm Modeller (GPT-4o, o1, vb.) |
| **Anthropic** | `Anthropic` | Tüm Modeller (Claude 3.5, Opus) |
| **Google** | `Google` | Tüm Modeller (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | Tüm Modeller (Llama 3, Mixtral) |
| **Azure** | `Azure` | Tüm Modeller (Enterprise) |
| **OpenRouter**| `OpenRouter`| Tüm Modeller (100+) |

---

## ⭐ Projeyi Destekleyin

Bu proje size zaman kazandırdıysa, lütfen GitHub'da bir yıldız vermeyi düşünün! Büyümemize yardımcı olur.

**[Bir Yıldız Verin!](https://github.com/Hosseinghorbani0/easyai)**

---
*Created by [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*
