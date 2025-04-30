import os
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# Read and store API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEBUI_BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MICROSOFT_API_KEY = os.getenv("MICROSOFT_API_KEY")
PONS_API_KEY = os.getenv("PONS_API_KEY")

# TODO all of the following vars are unused so far and just hardcoded
DEBUG = os.getenv("DEBUG")

# MAX_RETRIES = os.getenv("MAX_RETRIES")
# TEMPERATURE = os.getenv("TEMPERATURE")


