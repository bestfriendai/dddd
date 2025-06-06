# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Dict, Union
import os

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from src.config import load_yaml_config
from src.config.agents import LLMType
from src.llms.mock_llm import create_mock_llm

# Cache for LLM instances
_llm_cache: dict[LLMType, Union[ChatOpenAI, BaseChatModel]] = {}


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}_MODEL__{KEY}
    e.g., BASIC_MODEL__API_KEY, BASIC_MODEL__BASE_URL, BASIC_MODEL__MODEL
    """
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}

    import logging
    logger = logging.getLogger(__name__)

    # Debug: Log ALL environment variables to see what's available
    all_env_vars = list(os.environ.keys())
    logger.info(f"All environment variables: {all_env_vars}")

    # Log all environment variables that match our pattern for debugging
    matching_vars = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
    logger.info(f"Found environment variables for {llm_type}: {list(matching_vars.keys())}")

    # Also check for variations in case there's a naming issue
    alt_patterns = [
        f"{llm_type.upper()}_MODEL_",  # Single underscore
        f"{llm_type.lower()}_model__",  # Lowercase
        f"{llm_type.upper()}__",       # No MODEL part
    ]

    for pattern in alt_patterns:
        alt_matching = {k: v for k, v in os.environ.items() if k.startswith(pattern)}
        if alt_matching:
            logger.info(f"Found alternative pattern {pattern}: {list(alt_matching.keys())}")

    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix):].lower()
            conf[conf_key] = value
            logger.info(f"Mapped {key} -> {conf_key} = {value[:10]}...")

    return conf


def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> ChatOpenAI:
    # Map LLM types to configuration keys
    llm_type_map = {
        "reasoning": "REASONING_MODEL",
        "basic": "BASIC_MODEL",
        "vision": "VISION_MODEL",
    }

    config_key = llm_type_map.get(llm_type)
    if not config_key:
        raise ValueError(f"Unknown LLM type: {llm_type}")

    # Get configuration from YAML file
    llm_conf = conf.get(config_key, {})
    if not isinstance(llm_conf, dict):
        llm_conf = {}

    # Get configuration from environment variables
    env_conf = _get_env_llm_conf(llm_type)

    # Merge configurations, with environment variables taking precedence
    merged_conf = {**llm_conf, **env_conf}

    if not merged_conf:
        raise ValueError(f"No configuration found for LLM type: {llm_type}")

    # Ensure required parameters are present
    if "api_key" not in merged_conf:
        raise ValueError(f"Missing api_key for LLM type: {llm_type}")

    if "model" not in merged_conf:
        raise ValueError(f"Missing model for LLM type: {llm_type}")

    # Map configuration keys to ChatOpenAI parameter names
    chatgpt_params = {}
    for key, value in merged_conf.items():
        if key == "base_url":
            # ChatOpenAI expects openai_api_base instead of base_url
            chatgpt_params["openai_api_base"] = value
        elif key == "api_key":
            # ChatOpenAI expects openai_api_key instead of api_key
            chatgpt_params["openai_api_key"] = value
        else:
            chatgpt_params[key] = value

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating ChatOpenAI with parameters: {list(chatgpt_params.keys())}")

    # Add OpenRouter-specific headers if using OpenRouter
    if "openrouter.ai" in chatgpt_params.get("openai_api_base", ""):
        # Add required headers for OpenRouter using default_headers
        openrouter_headers = {
            "HTTP-Referer": "https://web-bestfriendais-projects.vercel.app",
            "X-Title": "AvaxSearch"
        }
        chatgpt_params["default_headers"] = openrouter_headers
        logger.info(f"Added OpenRouter headers via default_headers: {list(openrouter_headers.keys())}")

    # Create the ChatOpenAI instance
    llm = ChatOpenAI(**chatgpt_params)

    # Test the API key by making a simple call
    try:
        from langchain_core.messages import HumanMessage
        test_response = llm.invoke([HumanMessage(content="test")])
        logger.info("API key validation successful")
        return llm
    except Exception as api_error:
        logger.error(f"API key validation failed: {api_error}")
        # If API call fails, return mock LLM instead
        logger.warning(f"Falling back to mock LLM due to API error")
        return create_mock_llm()


def get_llm_by_type(
    llm_type: LLMType,
) -> Union[ChatOpenAI, BaseChatModel]:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    import logging
    logger = logging.getLogger(__name__)

    try:
        # Try to load configuration from YAML file
        conf_path = str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
        conf = load_yaml_config(conf_path)

        # Debug logging
        logger.info(f"Loading LLM config for type: {llm_type}")
        logger.info(f"Config file path: {conf_path}")
        logger.info(f"Config file exists: {os.path.exists(conf_path)}")
        logger.info(f"Available config keys: {list(conf.keys())}")

        # Also log environment variables for debugging
        env_conf = _get_env_llm_conf(llm_type)
        logger.info(f"Environment config for {llm_type}: {list(env_conf.keys())}")

        llm = _create_llm_use_conf(llm_type, conf)
        _llm_cache[llm_type] = llm
        return llm
    except Exception as e:
        logger.error(f"Failed to create LLM for type {llm_type}: {e}")

        # Try to create LLM using only environment variables as fallback
        try:
            logger.info(f"Attempting fallback: creating LLM using only environment variables for {llm_type}")
            env_conf = _get_env_llm_conf(llm_type)
            if env_conf:
                logger.info(f"Found environment config: {list(env_conf.keys())}")

                # Apply the same parameter mapping as in _create_llm_use_conf
                chatgpt_params = {}
                for key, value in env_conf.items():
                    if key == "base_url":
                        chatgpt_params["openai_api_base"] = value
                    elif key == "api_key":
                        chatgpt_params["openai_api_key"] = value
                    else:
                        chatgpt_params[key] = value

                # Add OpenRouter-specific headers if using OpenRouter
                if "openrouter.ai" in chatgpt_params.get("openai_api_base", ""):
                    # Add required headers for OpenRouter using default_headers
                    openrouter_headers = {
                        "HTTP-Referer": "https://web-bestfriendais-projects.vercel.app",
                        "X-Title": "AvaxSearch"
                    }
                    chatgpt_params["default_headers"] = openrouter_headers
                    logger.info(f"Added OpenRouter headers in fallback via default_headers: {list(openrouter_headers.keys())}")

                logger.info(f"Creating ChatOpenAI with fallback parameters: {list(chatgpt_params.keys())}")
                llm = ChatOpenAI(**chatgpt_params)
                _llm_cache[llm_type] = llm
                logger.info(f"Successfully created LLM using environment variables for {llm_type}")
                return llm
            else:
                logger.error(f"No environment configuration found for {llm_type}")
        except Exception as fallback_error:
            logger.error(f"Fallback also failed for {llm_type}: {fallback_error}")

        # Final fallback: use mock LLM for testing
        logger.warning(f"Using mock LLM for {llm_type} - no working API key found")
        mock_llm = create_mock_llm()
        _llm_cache[llm_type] = mock_llm
        return mock_llm


# In the future, we will use reasoning_llm and vl_llm for different purposes
# reasoning_llm = get_llm_by_type("reasoning")
# vl_llm = get_llm_by_type("vision")


if __name__ == "__main__":
    # Initialize LLMs for different purposes - now these will be cached
    basic_llm = get_llm_by_type("basic")
    print(basic_llm.invoke("Hello"))
