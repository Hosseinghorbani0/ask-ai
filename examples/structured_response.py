from dataclasses import dataclass

from ask_ai import OpenAI


@dataclass
class User:
    name: str
    age: int


response = OpenAI().ask(
    "Extract the user: Ada is 37.",
    response_model=User,
    validation_retries=2,
)
print(response.parsed)
