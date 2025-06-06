# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Mock LLM implementation for testing and fallback scenarios.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

logger = logging.getLogger(__name__)


class MockLLM(BaseChatModel):
    """
    A mock LLM implementation that returns predefined responses.
    Used for testing and as a fallback when real LLM APIs are unavailable.
    """

    model_name: str = "mock-llm"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initialized MockLLM")

    @property
    def _llm_type(self) -> str:
        return "mock"

    def bind_tools(self, tools, **kwargs):
        """
        Mock implementation of bind_tools method.
        Returns self to maintain compatibility with LangChain's tool binding interface.
        """
        logger.info(f"MockLLM: bind_tools called with {len(tools) if tools else 0} tools")
        # Return a copy of self to maintain the interface
        return self
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a mock response based on the input messages."""
        
        # Get the last human message
        last_message = ""
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                last_message = message.content
                break
        
        # Generate a simple mock response
        mock_response = self._generate_mock_response(last_message)
        
        # Create the response message
        response_message = AIMessage(content=mock_response)
        
        # Create the chat generation
        generation = ChatGeneration(message=response_message)
        
        return ChatResult(generations=[generation])
    
    def _generate_mock_response(self, input_text: str) -> str:
        """Generate a mock response based on the input text."""
        
        input_lower = input_text.lower()
        
        # Simple pattern matching for different types of queries
        if "search" in input_lower or "find" in input_lower:
            return "I'm a mock LLM. I would normally help you search for information, but I'm currently in testing mode. Please configure a real LLM API key for full functionality."
        
        elif "hello" in input_lower or "hi" in input_lower:
            return "Hello! I'm a mock LLM running in testing mode. To get real responses, please configure your LLM API keys."
        
        elif "test" in input_lower:
            return "Mock LLM test response successful!"
        
        elif "error" in input_lower:
            return "This is a mock error response for testing purposes."
        
        else:
            return f"Mock LLM received: '{input_text[:100]}...' - Please configure real LLM API keys for actual responses."
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async version of _generate."""
        return self._generate(messages, stop, run_manager, **kwargs)


def create_mock_llm(**kwargs) -> MockLLM:
    """
    Factory function to create a MockLLM instance.
    
    Args:
        **kwargs: Additional arguments to pass to the MockLLM constructor
        
    Returns:
        MockLLM: A configured mock LLM instance
    """
    logger.info("Creating MockLLM instance")
    return MockLLM(**kwargs)


if __name__ == "__main__":
    # Test the mock LLM
    mock_llm = create_mock_llm()
    
    # Test with a simple message
    from langchain_core.messages import HumanMessage
    
    test_messages = [HumanMessage(content="Hello, this is a test")]
    result = mock_llm._generate(test_messages)
    
    print("Mock LLM Test:")
    print(f"Input: {test_messages[0].content}")
    print(f"Output: {result.generations[0].message.content}")
