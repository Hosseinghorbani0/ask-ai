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
  <b>1行のコードでLLMプロバイダーを切り替えるための最小限のPython SDK。</b><br/>
  フレームワーク不要。 サーバー不要。 過剰な設計不要。
</p>

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ クイックスタート (5秒)

```bash
pip install askai-python
```

```python
from ask_ai import OpenAI, Groq

# 環境からOPENAI_API_KEYを自動検知
OpenAI().ask("5歳の子供に説明するようにブラックホールについて教えて").text

# プロバイダーを瞬時に切り替え
Groq().ask("5歳の子供に説明するようにブラックホールについて教えて").text
```

---

## 🧐 なぜ ask-ai なのか？

- **関数は1つだけ**: `.ask()` を呼び出すだけです。
- **マルチプロバイダー**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **ゼロコンフィグ**: キーは環境変数から自動的に取得されます。
- **SDKファースト、フレームワークではない**: 邪魔になることはありません。

## ⚖️ 比較

| 機能 | ask-ai | LangChain |
| -------------- | ------ | --------- |
| セットアップ時間 | 30秒 | 1時間 |
| 学習曲線 | ⭐ | ⭐⭐⭐⭐⭐ |
| Asyncサポート | ⏳ *(近日公開)* | ⚠️ 複雑 |
| リトライ/タイムアウト | ✅ 組み込み | ❌ 手動 |
| ゲートウェイが必要か | ❌ いいえ | ❌ いいえ |
| プロバイダー切り替え行数| **1** | 20+ |

## 🚫 このプロジェクトで「ない」もの

> ❌ AIフレームワークではありません
> ❌ APIゲートウェイではありません
> ❌ エージェントメモリーシステムではありません

ただ1つのことを完璧に行います：**LLMへのAPI呼び出しをシンプルにすること。**

---

## 🛠️ 高度な使い方

### 組み込みの耐障害性 (Retries & Timeout)
レート制限(`429`)やネットワークの切断を自動的に処理します：

```python
from ask_ai import OpenAI
ai = OpenAI()

# ネットワークエラー時に最大3回再試行し、デフォルトで10秒のタイムアウトを設定します
response = ai.ask("複雑なpythonスクリプトを書いて", retry=3, timeout=10)
```

### システム構成
システムプロンプトと温度(temperature)を直接設定します：

```python
ai.advanced(
    temperature=0.7,
    prompt="あなたはシニアDevOpsエンジニアです。"
)

print(ai.ask("Dockerfileを最適化するには？").text)
```

---

## 🔗 重要なリンク

- **GitHubリポジトリ**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (スターをお願いします！ ⭐)
- **PyPI**: [askai-python](https://pypi.org/project/askai-python/)
- **公式ウェブサイト**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
