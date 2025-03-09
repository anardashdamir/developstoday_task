import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# API Settings
API_TITLE = "Cocktail Advisor Chat"
API_DESCRIPTION = "A chat application that integrates with an LLM to create a RAG system for cocktail recommendations."
API_VERSION = "0.1.0"

# LLM Settings
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL")

# Vector DB Settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "cocktail-index")
PINECONE_NAMESPACE_COCKTAILS = None
PINECONE_NAMESPACE_USER_MEMORIES = "user-memories"

# Embedding Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# User memory detection settings
USER_PREFERENCE_PROMPT = """
You are a helpful assistant tasked with extracting information about a user's favorite cocktail ingredients and cocktails.

Analyze the following user message and extract any mentions of favorite ingredients or cocktails .
Return ONLY a valid JSON object with the following format:
{{"favorite_ingredients": ["ingredient1", "ingredient2", ...], "favorite_cocktails": ["cocktail1", "cocktail2", ...]}}

Both arrays should be empty if no favorites are mentioned. Do not include any explanations or other text outside the JSON.

User message: 
{message}

JSON Response:
"""