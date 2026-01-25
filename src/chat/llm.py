from openai import OpenAI
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

# https://github.com/openai/openai-agents-python
# https://cookbook.openai.com/examples/agents_sdk/session_memory#context-trimming


def ask_llm(system_prompt, messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.8
    )
    return response.choices[0].message.content