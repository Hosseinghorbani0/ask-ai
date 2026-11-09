# ask-ai

[![PyPI バージョン](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Python バージョン](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![MIT ライセンス](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**複数の LLM プロバイダーを一貫した API で呼び出す、小規模で型付けされた Python SDK です。**
大規模なオーケストレーションフレームワークを導入せず、スクリプトや Python アプリケーションから利用できます。

`ask-ai` はクライアントライブラリであり、ホスト型サービスやゲートウェイではありません。プロバイダークライアントを作成して同期または非同期で呼び出すと、共通の `Response` オブジェクトが返ります。プロバイダー SDK は任意依存のため、利用するものだけをインストールできます。

## ドキュメントの言語

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## 目次

- [機能](#機能)
- [要件とインストール](#要件とインストール)
- [プロバイダー](#プロバイダー)
- [クイックスタート](#クイックスタート)
- [公開 API](#公開-api)
- [リクエストオプション](#リクエストオプション)
- [リトライ、フォールバック、ルーティング](#リトライフォールバックルーティング)
- [構造化出力](#構造化出力)
- [ストリーミングと非同期利用](#ストリーミングと非同期利用)
- [メディア生成と安全なダウンロード](#メディア生成と安全なダウンロード)
- [会話セッションとクライアントのライフサイクル](#会話セッションとクライアントのライフサイクル)
- [機能情報と可観測性](#機能情報と可観測性)
- [アーキテクチャ](#アーキテクチャ)
- [コマンドライン](#コマンドライン)
- [互換性とトラブルシューティング](#互換性とトラブルシューティング)
- [コントリビューション、サポート、ライセンス](#コントリビューションサポートライセンス)

## 機能

- `ask`、`ask_async`、`ask_stream`、`ask_stream_async` の一貫した API。
- プロバイダーのフォールバックとポリシーベースのルーティング。
- 一時的な障害に対するリトライ、呼び出し単位および全体の期限。
- 型付き応答メタデータ、正規化されたトークン使用量、任意の可観測性フック。
- 対応プロバイダーでの JSON および検証付き構造化応答。
- 任意のインメモリ会話セッション。
- ローカルサーバーを含む OpenAI Chat Completions 互換エンドポイント。
- ポリシーで制御する安全なメディアダウンロード。

現在の公開リクエスト API が送信するのはテキストです。機能情報に vision 入力対応が示されるわけではありません。ツール呼び出しの実行や会話の永続保存は提供していません。

## 要件とインストール

- Python 3.10 以上。
- コアパッケージに必須依存関係はありません。プロバイダー SDK、メディア処理、構造化出力用ライブラリは任意の extra です。

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI、Azure OpenAI、OpenRouter、互換エンドポイント
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic と jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # 安全なメディアダウンロード
python -m pip install "askai-python[all]"
```

認証情報は環境変数に設定するか、プロバイダー作成時に `api_key=` で渡してください。ソースコードに秘密情報を記述しないでください。

## プロバイダー

| プロバイダー | Import | extra | 環境変数 | 既定モデル |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | Deployment の指定が必要 |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| OpenAI 互換 | `OpenAICompatibleProvider` | `openai` | なし（任意） | 作成時に必須 |

Azure では `AZURE_OPENAI_ENDPOINT` も必要です。deployment は `model=` または `AZURE_OPENAI_DEPLOYMENT_NAME` で指定します。`AZURE_OPENAI_API_VERSION` の既定値は `2024-06-01` です。互換プロバイダーには絶対 HTTP(S) URL の `base_url` とモデルが必要で、ローカル接続では `api_key` を省略できます。

`capabilities()` はテキスト、ストリーミング、非同期ストリーミング、構造化出力、ツール呼び出し、画像/音声生成、vision の宣言上の対応状況を返します。特定のモデルやアカウントで利用できる保証ではありません。ツール呼び出しの実行と vision 入力は、共通リクエスト機能として公開されていません。

## クイックスタート

```python
from ask_ai import OpenAI

client = OpenAI()  # OPENAI_API_KEY を読み込みます
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## 公開 API

| メソッド | 戻り値 | 説明 |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | 同期リクエスト |
| `await provider.ask_async(query, **options)` | `Response` | ネイティブ非同期リクエスト |
| `provider.ask_stream(query, **options)` | 文字列イテレーター | 同期テキストストリーム |
| `async for chunk in provider.ask_stream_async(...)` | 非同期イテレーター | 非同期テキストストリーム |
| `provider.ask_stream_events(...)` | イベントイテレーター | 型付き同期ストリーム |
| `provider.ask_stream_events_async(...)` | 非同期イベントイテレーター | 型付き非同期ストリーム |

`Response` は `text`、未加工の `raw`、解析済みの `json`、`response_model` を指定した場合の `parsed`/`pydantic`、任意の `media`、`usage`、`metadata` を提供します。`response.json` は応答テキストを解析します。JSON 形式を要求する場合は `json=True`、検証が必要な場合は `response_model=...` を使用してください。

## リクエストオプション

リクエストにオプションを渡すか、`provider.advanced(...)` で既定値を設定します。リクエスト側の値が優先されます。

| オプション | 用途 |
|---|---|
| `temperature`、`max_tokens`、`top_p` | 共通の生成制御 |
| `frequency_penalty`、`presence_penalty`、`stop` | プロバイダーが対応する生成制御 |
| `system_message`（別名: `system`、`prompt`） | システム指示 |
| `timeout` | 個別のプロバイダー呼び出しの上限（クライアントの既定値は30秒） |
| `total_timeout` | リトライを含む処理全体の期限 |
| `retry` | 追加リトライ回数。既定値2（最大3回の試行） |
| `json=True` | JSON形式を要求し、`response.json` で解析 |
| `response_model`、`validation_retries` | 対応する構造化モデルを解析・検証 |
| `output_type` | 対応する `image` または `audio` 出力を要求 |
| `clean`、`strip`、`code` | `response.text` の取得時にテキストを整形・抽出 |
| `strict_options=True` | 未知のオプションを警告ではなく例外にする |

個々のオプションへの対応はプロバイダー/モデルに依存します。未知のオプションは既定では警告され、strict モードでは `ValueError` になります。非推奨の `safe_mode` に定義済みの動作はありません。未対応の出力タイプは明示的なエラーになります。

## リトライ、フォールバック、ルーティング

一時的な再試行可能エラーでは、既定で2回リトライします（最大3試行）。無効なリクエストや認証エラーは再試行されません。`Retry-After` は最大30秒で適用されます。`timeout` は個々の呼び出し、`total_timeout` は全体の処理を制限します。

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

フォールバックは再試行可能なプロバイダーエラーの場合のみ次へ進みます。`Router` はポリシーに基づく選択と全体の `max_attempts` 上限を提供します。リトライやフォールバックは追加料金を発生させることがあります。チャンクを返した後のストリームは再試行されません。

## 構造化出力

Pydantic モデル、dataclass、`TypedDict`、JSON Schema に対応します。検証済みの値は `Response` の `.parsed` から取得します。

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

プロバイダーごとにネイティブ構造化出力の対応は異なります。検証はローカルで行われ、不正な出力では構造化検証エラーになります。セッションのストリーミングでは構造化検証を利用できません。

## ストリーミングと非同期利用

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

非同期呼び出しには `ask_async()`、`ask_stream_async()` を `await` / `async for` で利用します。現在のストリームイベントは `TextDelta`、`UsageUpdate`、`Completed`、`Error` です。`ToolCall` はイベント型として公開されていますが、現在のプロバイダーアダプターはツール呼び出しイベントを出力しません。イベントを受け取るには `ask_stream_events()` または `ask_stream_events_async()` を使います。キャンセルやプロバイダー例外はアプリケーション側で適切に処理してください。

## メディア生成と安全なダウンロード

一部のプロバイダーは `output_type="image"` または `"audio"` による生成に対応します。利用可否はプロバイダーとモデルによって異なります。現在のリクエスト API は vision 用画像入力を受け付けません。

安全なメディアダウンロードには `httpx` extra が必要です。既定では HTTPS を必須とし、リダイレクトと非公開 DNS アドレスを拒否し、25 MiB と30秒の上限を適用します。MIME タイプやホストを制限できます。

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

信頼できるプライベートネットワークの URL に限り `allow_private=True` を指定してください。ダウンロードポリシーを適用しても、取得した URL を他の用途で安全に利用できるとは限りません。

## 会話セッションとクライアントのライフサイクル

`provider.session()` で任意のインメモリ会話を作成できます。

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

履歴はプロセスメモリ内に保持され、永続化されません。`max_messages` はユーザー/アシスタントのペア単位で履歴を制限します。同時の同期呼び出し同士、非同期呼び出し同士は個別に直列化されます。同一セッションで同期/非同期操作を同時に混在させないでください。

プロバイダーには `close()`/`aclose()` と同期/非同期コンテキストマネージャーがあります。利用後はクライアントを閉じてください。キャッシュされた非同期クライアントは最初に使用した event loop に紐づくため、loop ごとにプロバイダーを作成します。

## 機能情報と可観測性

`provider.capabilities()` で宣言上の機能を確認できます。`provider.use(Observability(...))` で可観測性フックを登録すると、プロバイダー、モデル、レイテンシ、リトライ回数、正規化されたトークン使用量などを受け取れます。価格と使用量がそろう場合にのみ推定コストを算出します。

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

独自のテレメトリハンドラーにプロンプトや認証情報などの機密データを含めないでください。フックの例外はリクエストを中断しません。

## アーキテクチャ

`ask_ai` は共通プロバイダー基底クラス、SDK ごとのアダプター、共通 `Response`、任意の `Router` と `ConversationSession`、構造化出力およびメディアセキュリティのユーティリティで構成されています。SDK は任意インポートのため、すべての統合をインストールしなくてもパッケージを読み込めます。独自サービスを介してリクエストを中継することはありません。

## コマンドライン

インストールすると `ask-ai` コマンドが使えます。OpenAI、Groq、Google、OpenRouter、Azure、Anthropic に対応します。

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

CLI は選択したプロバイダーの環境変数認証情報を使います。OpenAI 互換プロバイダーは Python API から利用でき、現在の CLI 選択肢には含まれません。

## 互換性とトラブルシューティング

- **Python:** パッケージ分類では3.10～3.13、宣言された最低バージョンは3.10です。
- **型情報:** `ask_ai/py.typed` を同梱しています。
- **SDK がない:** 対応する extra（例: `askai-python[openai]`）をインストールしてください。
- **認証情報がない:** 上記の環境変数を設定するか `api_key=` を渡します。
- **Azure の初期化エラー:** endpoint、API キー、deployment/model を設定します。
- **未知のオプション:** 名前を確認するか `strict_options=True` を指定します。
- **event loop エラー:** 別の loop で非同期プロバイダーを再利用しないでください。
- **構造化出力が不正:** モデル/スキーマを確認し、追加課金を許容する場合だけ `validation_retries` を増やします。
- **実 API の動作:** モックテストでは実プロバイダーのモデル/オプション対応を保証しません。実 API テストは任意で、課金される場合があります。

## コントリビューション、サポート、ライセンス

不具合報告や機能要望は[課題トラッカー](https://github.com/Hosseinghorbani0/ask-ai/issues)へお寄せください。変更には対象を絞ったテストと、動作変更に対応するドキュメント更新を含めてください。送信前に `python -m pytest -q` と `ruff check .` を実行してください。[CHANGELOG.md](../CHANGELOG.md)も参照してください。

本プロジェクトは[MIT ライセンス](../LICENSE)で提供されます。問い合わせには最小限の再現例を添え、API キー、個人情報、その他の秘密情報を必ず削除してください。[PyPI](https://pypi.org/project/askai-python/) と[GitHub リポジトリ](https://github.com/Hosseinghorbani0/ask-ai)もご覧ください。
