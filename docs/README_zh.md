# ask-ai

[![PyPI 版本](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Python 版本](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![MIT 许可证](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

**一个小巧、带类型的 Python SDK，通过统一 API 调用多个 LLM 提供商。**
可在脚本和 Python 应用中使用，无需引入庞大的编排框架。

`ask-ai` 是客户端库，不是托管服务或网关。创建提供商客户端后，可同步或异步调用，并获得统一的 `Response` 对象。提供商 SDK 为可选依赖，只安装实际需要的即可。

## 文档语言

[English](../README.md) · [العربية](README_ar.md) · [فارسی](README_fa.md) · [Español](README_es.md) · [日本語](README_ja.md) · [Русский](README_ru.md) · [Türkçe](README_tr.md) · [中文](README_zh.md)

## 目录

- [功能](#功能)
- [要求与安装](#要求与安装)
- [提供商](#提供商)
- [快速开始](#快速开始)
- [公共 API](#公共-api)
- [请求选项](#请求选项)
- [重试、回退与路由](#重试回退与路由)
- [结构化输出](#结构化输出)
- [流式与异步用法](#流式与异步用法)
- [媒体生成与安全下载](#媒体生成与安全下载)
- [会话与客户端生命周期](#会话与客户端生命周期)
- [能力与可观测性](#能力与可观测性)
- [架构](#架构)
- [命令行界面](#命令行界面)
- [兼容性与故障排查](#兼容性与故障排查)
- [贡献、支持与许可证](#贡献支持与许可证)

## 功能

- 统一的 `ask`、`ask_async`、`ask_stream` 和 `ask_stream_async` API。
- 提供商回退与基于策略的路由。
- 针对临时故障重试，并支持单次调用与整体截止时间。
- 带类型的响应元数据、标准化 token 用量和可选的可观测性钩子。
- 支持的提供商可返回 JSON 和经过验证的结构化响应。
- 可选的内存会话。
- 兼容 OpenAI Chat Completions 的端点，包括本地服务。
- 由策略控制的安全媒体下载。

当前公共请求 API 发送文本；能力信息不代表支持视觉图像输入。本库不提供工具调用执行或持久化会话存储。

## 要求与安装

- Python 3.10 或更高版本。
- 核心包没有必需依赖。提供商 SDK、媒体和结构化输出库均为可选 extras。

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI、Azure OpenAI、OpenRouter、兼容端点
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic 和 jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # 安全媒体下载
python -m pip install "askai-python[all]"
```

将凭据放入环境变量，或在创建提供商时传入 `api_key=`。不要把密钥写入源代码。

## 提供商

| 提供商 | 导入名 | Extra | 环境变量 | 默认模型 |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | 必须指定 Deployment |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| OpenAI 兼容 | `OpenAICompatibleProvider` | `openai` | 无（可选） | 创建时必填 |

Azure 还需要 `AZURE_OPENAI_ENDPOINT`。Deployment 可通过 `model=` 或 `AZURE_OPENAI_DEPLOYMENT_NAME` 指定；`AZURE_OPENAI_API_VERSION` 默认为 `2024-06-01`。兼容提供商需要绝对 HTTP(S) `base_url` 和模型；本地端点可省略 `api_key`。

`capabilities()` 返回文本、流式、异步流式、结构化输出、工具调用、图像/音频生成及视觉能力的声明值。这不保证特定模型或账户实际支持。工具调用执行和视觉输入并非通用请求功能。

## 快速开始

```python
from ask_ai import OpenAI

client = OpenAI()  # 读取 OPENAI_API_KEY
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

## 公共 API

| 方法 | 返回值 | 说明 |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | 同步请求 |
| `await provider.ask_async(query, **options)` | `Response` | 原生异步请求 |
| `provider.ask_stream(query, **options)` | 字符串迭代器 | 同步文本流 |
| `async for chunk in provider.ask_stream_async(...)` | 异步迭代器 | 异步文本流 |
| `provider.ask_stream_events(...)` | 事件迭代器 | 带类型的同步事件流 |
| `provider.ask_stream_events_async(...)` | 异步事件迭代器 | 带类型的异步事件流 |

`Response` 提供 `text`、未修改的 `raw`、解析后的 `json`，以及指定 `response_model` 时的 `parsed`/`pydantic`，还包括可选的 `media`、`usage` 和 `metadata`。`response.json` 解析响应文本；用 `json=True` 请求 JSON 格式，用 `response_model=...` 执行模型验证。

## 请求选项

可在请求中传入选项，或通过 `provider.advanced(...)` 设置默认值；请求级选项优先。

| 选项 | 用途 |
|---|---|
| `temperature`、`max_tokens`、`top_p` | 常见生成参数 |
| `frequency_penalty`、`presence_penalty`、`stop` | 由提供商支持的生成参数 |
| `system_message`（别名 `system`、`prompt`） | 系统指令 |
| `timeout` | 单次提供商调用超时（客户端默认 30 秒） |
| `total_timeout` | 包含重试在内的整体截止时间 |
| `retry` | 额外重试次数；默认 2 次（最多 3 次尝试） |
| `json=True` | 请求 JSON 格式，可通过 `response.json` 解析 |
| `response_model`、`validation_retries` | 解析并验证受支持的结构化模型 |
| `output_type` | 请求受支持的 `image` 或 `audio` 输出 |
| `clean`、`strip`、`code` | 读取 `response.text` 时清理或提取文本 |
| `strict_options=True` | 未知选项直接报错，而非仅警告 |

选项支持情况因提供商和模型而异。未知选项默认发出警告；严格模式会抛出 `ValueError`。已弃用的 `safe_mode` 没有定义行为。不支持的输出类型会明确报错。

## 重试、回退与路由

对于可重试的临时故障，默认额外重试两次（最多三次尝试）。无效请求和认证错误不会重试。`Retry-After` 会遵循，但最多等待 30 秒。`timeout` 限制单次调用，`total_timeout` 限制整个操作。

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

只有遇到可重试的提供商错误时才会切换到下一个提供商。`Router` 提供基于策略的选择和整体 `max_attempts` 上限。重试或回退可能增加费用；流式输出已产生内容后不会重试。

## 结构化输出

支持 Pydantic 模型、dataclass、`TypedDict` 和 JSON Schema。返回普通 `Response`，通过 `.parsed` 读取验证后的结果。

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

提供商原生结构化输出支持不尽相同；验证在本地执行。无效输出会引发结构化验证错误。会话流式方法不支持结构化验证。

## 流式与异步用法

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

异步调用可通过 `await` 和 `async for` 使用 `ask_async()`、`ask_stream_async()`。当前流事件包括 `TextDelta`、`UsageUpdate`、`Completed` 和 `Error`。`ToolCall` 已作为事件类型导出，但当前提供商适配器不会发出工具调用事件。使用 `ask_stream_events()` 或 `ask_stream_events_async()` 接收事件。应用应按需处理取消和提供商异常。

## 媒体生成与安全下载

部分提供商支持通过 `output_type="image"` 或 `"audio"` 生成媒体；具体支持取决于提供商和模型。当前请求 API 不接受用于视觉理解的图像输入。

安全媒体下载需要 `httpx` extra。默认要求 HTTPS，拒绝重定向和非公网 DNS 地址，并限制为 25 MiB 和 30 秒。可进一步限制 MIME 类型和主机：

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(max_bytes=10 * 1024 * 1024,
                allowed_mime_types={"image/png"},
                allowed_hosts={"example.com"}),
)
```

只有在信任私有网络主机时才设置 `allow_private=True`。下载策略并不意味着任意提供商生成的 URL 都适合其他用途。

## 会话与客户端生命周期

`provider.session()` 创建可选的内存会话：

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

历史仅保存在进程内，不会持久化。`max_messages` 按用户/助手消息对限制历史。同一会话中的并发同步调用会彼此串行化，异步调用亦然；不要在同一会话上并发混用同步和异步操作。

提供商支持 `close()`/`aclose()` 及同步/异步上下文管理器。用完后关闭客户端。缓存的异步客户端绑定首次使用它的事件循环；每个循环应创建独立提供商实例。

## 能力与可观测性

通过 `provider.capabilities()` 查看声明能力。使用 `provider.use(Observability(...))` 注册可观测性钩子，可接收提供商、模型、延迟、重试次数和标准化 token 用量等信息。只有提供定价且供应商报告用量时才会估算成本。

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

不要在自定义遥测处理程序中记录密钥或敏感提示。钩子异常不会中断请求。

## 架构

`ask_ai` 包含共享提供商基类、提供商 SDK 适配器、统一 `Response`、可选的 `Router` 与 `ConversationSession`，以及结构化输出和媒体安全工具。SDK 采用可选导入，因此无需安装全部集成即可导入包。本库不会通过自有服务转发请求。

## 命令行界面

安装后可使用 `ask-ai` 命令，支持 OpenAI、Groq、Google、OpenRouter、Azure 和 Anthropic：

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

CLI 使用所选提供商的环境凭据。通用 OpenAI 兼容提供商可通过 Python API 使用，目前不在 CLI 的提供商选项中。

## 兼容性与故障排查

- **Python：** 包分类器列出 3.10–3.13，声明的最低版本为 3.10。
- **类型信息：** 发布包包含 `ask_ai/py.typed`。
- **缺少 SDK：** 安装相应 extra，例如 `askai-python[openai]`。
- **缺少凭据：** 设置上表中的环境变量，或传入 `api_key=`。
- **Azure 初始化失败：** 配置 endpoint、密钥和 deployment/model。
- **未知选项：** 检查拼写，或使用 `strict_options=True`。
- **事件循环错误：** 不要跨事件循环复用异步提供商客户端。
- **结构化输出无效：** 检查模型/Schema；增加验证重试可能产生额外费用。
- **真实服务行为：** Mock 测试不能保证线上模型接受某个选项；真实集成测试可能产生费用。

## 贡献、支持与许可证

请通过[问题跟踪器](https://github.com/Hosseinghorbani0/ask-ai/issues)报告缺陷或提出功能建议。代码贡献应包含针对性测试，并在行为变化时更新文档。提交前运行 `python -m pytest -q` 和 `ruff check .`；版本记录见 [CHANGELOG.md](../CHANGELOG.md)。

本项目采用 [MIT 许可证](../LICENSE)。提交支持请求时请提供最小复现示例，并删除 API 密钥、个人信息和其他秘密。更多信息见 [PyPI](https://pypi.org/project/askai-python/) 和 [GitHub 仓库](https://github.com/Hosseinghorbani0/ask-ai)。
