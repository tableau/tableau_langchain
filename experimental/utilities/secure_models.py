"""
Secure wrappers for LangChain models with usage tracking and cost monitoring.
Use these instead of direct model instantiation to track OpenAI costs.
"""
import os
from typing import Optional, Any, Dict
from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings
from langchain.callbacks.base import BaseCallbackHandler
import logging

logger = logging.getLogger(__name__)


class UsageCallbackHandler(BaseCallbackHandler):
    """Callback handler to track token usage and costs."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0

        # Approximate costs per 1K tokens (update as needed)
        self.costs = {
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4o': {'input': 0.0025, 'output': 0.01},
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'text-embedding-3-small': {'input': 0.00002, 'output': 0},
            'text-embedding-3-large': {'input': 0.00013, 'output': 0}
        }

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Track token usage after LLM call completes."""
        if hasattr(response, 'llm_output') and response.llm_output:
            usage = response.llm_output.get('token_usage', {})

            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)

            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.total_tokens += total_tokens

            # Calculate cost
            costs = self.costs.get(self.model_name, self.costs['gpt-4o-mini'])
            input_cost = (prompt_tokens / 1000) * costs['input']
            output_cost = (completion_tokens / 1000) * costs['output']
            call_cost = input_cost + output_cost

            self.total_cost += call_cost

            logger.info(
                f"LLM Usage - Model: {self.model_name}, "
                f"Tokens: {prompt_tokens} + {completion_tokens} = {total_tokens}, "
                f"Cost: ${call_cost:.6f} (Total: ${self.total_cost:.6f})"
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary."""
        return {
            'model': self.model_name,
            'total_tokens': self.total_tokens,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_cost_usd': round(self.total_cost, 6)
        }


def select_model_with_tracking(
    provider: str = "openai",
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    track_usage: bool = True
) -> BaseChatModel:
    """
    Create a LangChain chat model with automatic usage tracking.

    Args:
        provider: Model provider ('openai' or 'azure')
        model_name: Name of the model to use
        temperature: Temperature for response generation
        max_tokens: Maximum tokens in response (optional)
        track_usage: Whether to track token usage and costs

    Returns:
        Configured chat model with usage tracking
    """
    callbacks = []
    if track_usage:
        usage_handler = UsageCallbackHandler(model_name)
        callbacks.append(usage_handler)
        logger.info(f"Initializing {provider} model '{model_name}' with usage tracking")

    if provider == "azure":
        model = AzureChatOpenAI(
            azure_deployment=os.environ.get("AZURE_OPENAI_AGENT_DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=f"https://{os.environ.get('AZURE_OPENAI_API_INSTANCE_NAME')}.openai.azure.com",
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=callbacks
        )
    else:  # default to OpenAI
        model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            callbacks=callbacks
        )

    # Attach usage handler to model for later retrieval
    if track_usage:
        model._usage_handler = usage_handler

    return model


def select_embeddings_with_tracking(
    provider: str = "openai",
    model_name: str = "text-embedding-3-small",
    track_usage: bool = True
) -> Embeddings:
    """
    Create embeddings model with usage tracking.

    Args:
        provider: Model provider ('openai' or 'azure')
        model_name: Name of the embedding model
        track_usage: Whether to track usage

    Returns:
        Configured embeddings model
    """
    if track_usage:
        logger.info(f"Initializing {provider} embeddings '{model_name}' with usage tracking")

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


def get_usage_summary(model: BaseChatModel) -> Optional[Dict[str, Any]]:
    """
    Get usage summary from a tracked model.

    Args:
        model: The model instance to get usage from

    Returns:
        Usage summary dict or None if tracking is not enabled
    """
    if hasattr(model, '_usage_handler'):
        return model._usage_handler.get_summary()
    return None


# Convenience function for backwards compatibility
select_model = select_model_with_tracking
select_embeddings = select_embeddings_with_tracking

