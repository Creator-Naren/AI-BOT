from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key, model="gpt-4o-mini", base_url=None, system_prompt="You are a helpful AI assistant."):
        self.model = model
        self.system_prompt = system_prompt
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    def generate_reply(self, message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
        )
        return (response.choices[0].message.content or "").strip()
