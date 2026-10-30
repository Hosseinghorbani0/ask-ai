from ask_ai import Groq, OpenAI, Router

router = Router(
    [OpenAI(), Groq()],
    policy="fastest",
    profiles={
        "OpenAIProvider": {"latency_ms": 900},
        "GroqProvider": {"latency_ms": 250},
    },
)
print(router.ask("Explain routing in one sentence").text)
