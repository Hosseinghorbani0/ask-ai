from ask_ai import Observability
from ask_ai.base import BaseProvider, Response


class ObservableProvider(BaseProvider):
    def _get_api_key_env_var(self):
        return "TEST_API_KEY"

    def _get_default_model(self):
        return "test-model"

    def _send_request(self, messages, config, output_type=None):
        return Response("ok")


def test_observability_attaches_metadata_and_cost():
    events = []
    provider = ObservableProvider(api_key="test").use(
        Observability(
            on_event=events.append,
            pricing={"test-model": {"input": 1.0, "output": 2.0}},
        )
    )

    response = provider.ask("hello")

    assert response.metadata.provider == "ObservableProvider"
    assert response.metadata.model == "test-model"
    assert response.metadata.latency_ms >= 0
    assert response.metadata.retry_count == 0
    assert events[0]["type"] == "completed"


def test_observability_cost_uses_usage():
    middleware = Observability(pricing={"model": {"input": 10.0, "output": 20.0}})
    cost = middleware.cost("model", {"input_tokens": 1000, "output_tokens": 500})
    assert cost == 0.02


def test_observability_assigns_estimated_cost_to_response_metadata():
    class UsageProvider(ObservableProvider):
        def _send_request(self, messages, config, output_type=None):
            response = Response("ok")
            response.usage = {"input_tokens": 1000, "output_tokens": 500}
            return response

    provider = UsageProvider(api_key="test").use(
        Observability(pricing={"test-model": {"input": 1.0, "output": 2.0}})
    )

    response = provider.ask("hello")

    assert response.metadata.estimated_cost == 0.002
