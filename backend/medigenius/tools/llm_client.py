import os
import sys
import logging
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

logger = logging.getLogger("medigenius.llm_client")

# Load .env from backend root (two levels up from tools/)
_backend_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
_env_path = os.path.join(_backend_root, ".env")
load_dotenv(_env_path)

if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)


class BytezChatModel(BaseChatModel):
    """Custom LangChain ChatModel that uses Bytez API (Gemini 2.5 Flash)."""

    model_name: str = "google/gemini-2.5-flash"
    temperature: float = 0.3
    max_tokens: int = 2048

    @property
    def _llm_type(self) -> str:
        return "bytez"

    def _generate(self, messages: list[BaseMessage], stop=None, **kwargs) -> ChatResult:
        from services.bytez_client import call_bytez_chat

        msg_dicts = []
        for m in messages:
            if m.type == "human":
                msg_dicts.append({"role": "user", "content": m.content})
            elif m.type == "ai":
                msg_dicts.append({"role": "assistant", "content": m.content})
            elif m.type == "system":
                msg_dicts.append({"role": "user", "content": m.content})
            else:
                msg_dicts.append({"role": "user", "content": m.content})

        text = call_bytez_chat(msg_dicts, temperature=self.temperature, max_tokens=self.max_tokens)
        if not text:
            text = "I'm sorry, I couldn't generate a response at this time."

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])


# Global LLM instance
_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = BytezChatModel(
            temperature=0.3,
            max_tokens=2048
        )
    return _llm_instance
