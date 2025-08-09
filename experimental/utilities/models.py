import os

from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings


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
    elif provider == "aws":
        auth_type = 'profile' if os.environ.get("aws_cred_profile",None) is None else 'creds'
        if auth_type == 'profile':
            return ChatBedrockConverse(
                model=model_name,
                temperature=temperature,
                credentials_profile_name = os.environ.get("aws_cred_profile")
            )
        else:
            return ChatBedrockConverse(
                model=model_name,
                temperature=temperature,
                aws_access_key_id=os.environ.get("aws_access_key_id"),
                aws_secret_access_key=os.environ.get("aws_secret_access_key"),
                aws_session_token=os.environ.get("aws_session_token")
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
    elif provider == "aws":
        auth_type = 'profile' if os.environ.get("aws_cred_profile",None) is None else 'creds'
        if auth_type == 'profile':

            return BedrockEmbeddings(
                model=model_name,
                credentials_profile_name = os.environ.get("aws_cred_profile")
            )
        else:
            return BedrockEmbeddings(
                model=model_name,
                aws_access_key_id=os.environ.get("aws_access_key_id"),
                aws_secret_access_key=os.environ.get("aws_secret_access_key"),
                aws_session_token=os.environ.get("aws_session_token")
            )
    else:  # default to OpenAI
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
