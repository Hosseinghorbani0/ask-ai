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
  <b>たった1行のコードでLLMプロバイダーを切り替える、最小構成のPython SDK。</b><br/>
  フレームワーク不要。サーバー不要。過剰な設計不要。
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

# 環境変数からOPENAI_API_KEYを自動検出します
OpenAI().ask("5歳の子供に説明するようにブラックホールを説明して").text

# プロバイダーを瞬時に切り替え
Groq().ask("5歳の子供に説明するようにブラックホールを説明して").text
```

---

## 🧐 なぜ ask-ai なのか？

- **関数は1つだけ**: `.ask()` を呼び出すだけです。
- **複数のプロバイダー**: OpenAI, Anthropic, Google Gemini, Groq, Azure, OpenRouter
- **設定ゼロ**: キーはOSの環境変数から自動的に取得されます。
- **フレームワークではなく、SDKファースト**: あなたのコードやアーキテクチャの邪魔をしません。

## 🚫 このプロジェクトで「ない」もの

> ❌ 巨大なAIフレームワークではありません。
> ❌ APIゲートウェイではありません。
> ❌ エージェントメモリーシステムではありません。

このプロジェクトは、ただ一つのことを完璧にこなします：**LLMへのAPI呼び出しを単純化すること。**

---

## 🛠️ 高度な使い方

### 🧰 開発者向けツール (Auto-Parsing)
モデルの出力をクリーンアップするために正規表現を書くのはやめましょう！ `ask-ai` には組み込みのパースフラグがあります：

```python
from ask_ai import OpenAI
ai = OpenAI()

# 1. Clean Markdown (```json などのMarkdownコードブロックを削除)
clean_text = ai.ask("Write JSON", clean=True).text

# 2. Extract Code (コードブロックのみを抽出し、AIの無駄な会話を無視)
code = ai.ask("Write a python script", code=True).text

# 3. Strip Tags (<think>ブロックやHTMLタグを削除)
answer_only = ai.ask("What is 1+1?", strip=True).text

# 4. Enforce & Parse JSON (パースされたPython辞書を直接返す)
data_dict = ai.ask("Extract info", json=True).json
print(data_dict['name'])
```

### 🔄 内蔵の再試行とタイムアウト (Resiliency)
レート制限 (`429`) やネットワークの切断を指数的バックオフで自動的に処理します：

```python
# ネットワークエラー時に最大3回再試行し、タイムアウトを10秒に設定
response = ai.ask("Pythonスクリプトを書いて", retry=3, timeout=10)
```

### ⚙ システム設定
システムプロンプトやtemperature（クリエイティビティレベル）を直接設定：

```python
ai.advanced(
    temperature=0.7,
    prompt="あなたはシニアDevOpsエンジニアです。"
)

print(ai.ask("Dockerfileを最適化するにはどうすればいいですか？").text)
```

---

## 🔗 重要なリンク

- **GitHub リポジトリ**: [Hosseinghorbani0/ask-ai](https://github.com/Hosseinghorbani0/ask-ai) (ぜひスター⭐をつけてください！)
- **PyPI パッケージ**: [askai-python](https://pypi.org/project/askai-python/)
- **公式ウェブサイト**: [hosseinghorbani0.ir](https://hosseinghorbani0.ir/)
