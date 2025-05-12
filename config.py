import os
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# Read and store API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BLABLADOR_API_KEY = os.getenv("BLABLADOR_API_KEY")
BLABLADOR_BASE_URL = os.getenv("BLABLADOR_BASE_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
MICROSOFT_API_KEY = os.getenv("MICROSOFT_API_KEY")
MICROSOFT_REGION = os.getenv("MICROSOFT_REGION")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY")
OPENWEBUI_BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
PONS_API_KEY = os.getenv("PONS_API_KEY")

DEBUG = os.getenv("DEBUG")
