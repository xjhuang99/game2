import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# DeepSeek chat API is OpenAI-compatible; use deepseek-chat for general dialogue.
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_CHAT_MODEL = "deepseek-chat"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_CHAT_MODEL = "gemini-2.5-flash"

OPENAI_TO_DEEPSEEK = {
    "gpt-4o-mini": DEEPSEEK_CHAT_MODEL,
    "gpt-5": DEEPSEEK_CHAT_MODEL,
    "gpt-4o": DEEPSEEK_CHAT_MODEL,
    "gpt-4": DEEPSEEK_CHAT_MODEL,
    "gpt-3.5-turbo": DEEPSEEK_CHAT_MODEL,
}


def map_model_for_deepseek(model: str) -> str:
    return OPENAI_TO_DEEPSEEK.get(model, DEEPSEEK_CHAT_MODEL)


class ChatLLMService:
    """Try OpenAI, then Gemini, then DeepSeek."""

    def __init__(self, service_name: str = "LLM"):
        self.service_name = service_name
        self.openai_client = None
        self.gemini_client = None
        self.deepseek_client = None

        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            print(f"✅ [{self.service_name}] OpenAI ready.")

        gemini_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
        if gemini_key:
            self.gemini_client = OpenAI(api_key=gemini_key, base_url=GEMINI_BASE_URL)
            print(f"✅ [{self.service_name}] Gemini ready ({GEMINI_CHAT_MODEL}).")

        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if deepseek_key:
            self.deepseek_client = OpenAI(
                api_key=deepseek_key,
                base_url=DEEPSEEK_BASE_URL,
            )
            print(f"✅ [{self.service_name}] DeepSeek ready ({DEEPSEEK_CHAT_MODEL}).")

        if not self.openai_client and not self.gemini_client and not self.deepseek_client:
            print(f"⚠️ [{self.service_name}] No OpenAI, Gemini, or DeepSeek API key.")

    @property
    def available(self) -> bool:
        return bool(self.openai_client or self.gemini_client or self.deepseek_client)

    def chat_completion(
        self,
        messages,
        model: str = "gpt-4o",
        max_completion_tokens: int = 600,
    ) -> str:
        if not self.available:
            raise RuntimeError("No LLM API key configured (OpenAI, Gemini, or DeepSeek).")

        attempts = []
        if self.openai_client:
            attempts.append(("OpenAI", self.openai_client, model))
        if self.gemini_client:
            attempts.append(("Gemini", self.gemini_client, GEMINI_CHAT_MODEL))
        if self.deepseek_client:
            attempts.append(
                ("DeepSeek", self.deepseek_client, map_model_for_deepseek(model))
            )

        last_error = None
        for provider_name, client, use_model in attempts:
            try:
                response = client.chat.completions.create(
                    model=use_model,
                    messages=messages,
                    max_completion_tokens=max_completion_tokens,
                )
                content = (response.choices[0].message.content or "").strip()
                print(f"✅ [{self.service_name}] {provider_name} ({use_model})")
                return content
            except Exception as e:
                last_error = e
                print(f"⚠️ [{self.service_name}] {provider_name} failed: {e}")

        raise last_error or RuntimeError("All LLM providers failed.")
