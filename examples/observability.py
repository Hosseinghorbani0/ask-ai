from ask_ai import Observability, OpenAI


def print_event(event):
    metadata = event["metadata"]
    print(
        f"{metadata.provider}/{metadata.model} "
        f"{metadata.latency_ms:.0f}ms cost={metadata.estimated_cost}"
    )


ai = OpenAI().use(
    Observability(
        on_event=print_event,
        pricing={"gpt-4o": {"input": 5.0, "output": 15.0}},
    )
)
print(ai.ask("Explain observability in one sentence").text)
