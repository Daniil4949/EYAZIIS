from dataclasses import dataclass

from openai import OpenAI

from app.service.logical_search.service import LogicalSearchService


@dataclass
class OpenAIService:
    logical_search_service: LogicalSearchService
    open_ai_token: str

    async def getting_response_from_open_ai(self, query):
        client = OpenAI(api_key=self.open_ai_token)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return chat_completion.choices[0].message.content
