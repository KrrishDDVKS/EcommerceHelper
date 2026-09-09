from openai import AsyncOpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import os

# Initialize OpenAI client with LangSmith wrapper
client = wrap_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))

