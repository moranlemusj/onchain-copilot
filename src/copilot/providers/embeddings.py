from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ..config import settings

embeddings = GoogleGenerativeAIEmbeddings(
    model=settings.gemini_embedding_model,
    google_api_key=settings.google_api_key,
)
