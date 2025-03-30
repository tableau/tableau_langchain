import os

from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings


def select_model(provider: str = "openai", model_name: str = "gpt-4o-mini", temperature: float = 0.2) -> BaseChatModel:
    if provider == "azure":
        return AzureChatOpenAI(
            azure_deployment=os.environ.get("AZURE_OPENAI_AGENT_DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=f"https://{os.environ.get('AZURE_OPENAI_API_INSTANCE_NAME')}.openai.azure.com",
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            model_name=model_name,
            temperature=temperature
        )
    else:  # default to OpenAI
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )


def select_embeddings(provider: str = "openai", model_name: str = "text-embedding-3-small") -> Embeddings:
    if provider == "azure":
        return AzureOpenAIEmbeddings(
            azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=f"https://{os.environ.get('AZURE_OPENAI_API_INSTANCE_NAME')}.openai.azure.com",
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            model=model_name
        )
    else:  # default to OpenAI
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
