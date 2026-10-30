from ask_ai import OpenAI

session = OpenAI().session(max_messages=20)
print(session.ask("My name is Ada.").text)
print(session.ask("What is my name?").text)
