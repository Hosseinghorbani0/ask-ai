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

**AIをシンプルに。**
たった1行のコードでOpenAI、Groq、Google、Anthropicなどに接続できます。

> プロバイダーごとにAIコードを書き直すのはやめましょう。1行だけ使いましょう。いつでもモデルを切り替えられます。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ なぜ easyai なのか？

- **SDKロックインなし**: 5つの異なるライブラリを学ぶ必要はありません。1つだけ学びましょう。
- **統一API**: `ai.ask()` はすべてのプロバイダーでテキスト、画像、音声に対して機能します。
- **本番環境対応**: 組み込みの型安全性、エラー処理、環境管理。
- **ゼロ設定**: 環境からAPIキーを自動的に検出します。

---

## 🚀 黄金の例 (The Golden Example)

たった3行のコードで `easyai` の力を体験してください：

```python
from easyai import OpenAI, Anthropic, Google

prompt = "量子コンピュータを一行で説明して。"

# プロバイダーを瞬時に切り替え
print("OpenAI:   ", OpenAI().ask(prompt))
print("Claude:   ", Anthropic().ask(prompt))
print("Gemini:   ", Google().ask(prompt))
```

---

## 📦 インストール

```bash
pip install easyai
```

---

## 📖 クイックスタートガイド

### 1. 設定
APIキーをエクスポート（または明示的に渡す）します。
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. 標準的な使用法
```python
from easyai import OpenAI

ai = OpenAI()
print(ai.ask("こんにちは、世界！"))
```

### 3. 高度な使用法 (プロフェッショナル)
`temperature`、`top_p`、システムペルソナ (`prompt`) を制御して、プロフェッショナルな結果を得ます。

```python
ai.advanced(
    temperature=0.7,
    prompt="あなたはシニアDevOpsエンジニアです。"
)

print(ai.ask("Dockerfileを最適化するにはどうすればいいですか？"))
```

---

## 🔌 サポートされているプロバイダー

| プロバイダー | クラス | 機能セット |
|----------|-------|-------------|
| **OpenAI** | `OpenAI` | 全モデル対応 (GPT-4o, o1, etc.) |
| **Anthropic** | `Anthropic` | 全モデル対応 (Claude 3.5, Opus) |
| **Google** | `Google` | 全モデル対応 (Gemini 1.5 Pro/Flash) |
| **Groq** | `Groq` | 全モデル対応 (Llama 3, Mixtral) |
| **Azure** | `Azure` | 全モデル対応 (Enterprise) |
| **OpenRouter**| `OpenRouter`| 全モデル対応 (100+) |

---

## ⭐ プロジェクトをサポート

このプロジェクトが時間の節約になった場合は、GitHubでスターを付けることを検討してください！私たちの成長に役立ちます。

**[スターを付ける！](https://github.com/Hosseinghorbani0/easyai)**

---
*Created by [Hossein Ghorbani](https://hosseinghorbani0.ir/) | [GitHub](https://github.com/Hosseinghorbani0).*
