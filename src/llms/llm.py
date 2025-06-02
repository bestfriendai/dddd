# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Dict
import os

from langchain_openai import ChatOpenAI

from src.config import load_yaml_config
from src.config.agents import LLMType

# Cache for LLM instances
_llm_cache: dict[LLMType, ChatOpenAI] = {}


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}__{KEY}
    e.g., BASIC_MODEL__api_key, BASIC_MODEL__base_url
    """
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
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

    return ChatOpenAI(**merged_conf)


def get_llm_by_type(
    llm_type: LLMType,
) -> ChatOpenAI:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    try:
        conf_path = str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
        conf = load_yaml_config(conf_path)

        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Loading LLM config for type: {llm_type}")
        logger.debug(f"Config file path: {conf_path}")
        logger.debug(f"Available config keys: {list(conf.keys())}")

        llm = _create_llm_use_conf(llm_type, conf)
        _llm_cache[llm_type] = llm
        return llm
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create LLM for type {llm_type}: {e}")
        raise


# In the future, we will use reasoning_llm and vl_llm for different purposes
# reasoning_llm = get_llm_by_type("reasoning")
# vl_llm = get_llm_by_type("vision")


if __name__ == "__main__":
    # Initialize LLMs for different purposes - now these will be cached
    basic_llm = get_llm_by_type("basic")
    print(basic_llm.invoke("Hello"))
