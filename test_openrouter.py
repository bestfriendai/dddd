#!/usr/bin/env python3
"""
Quick test to verify OpenRouter API is working with correct model IDs.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_direct():
    """Test OpenRouter API directly."""
    try:
        from openai import OpenAI
        
        # Use your API key
        api_key = "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"
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        print("🔍 Testing OpenRouter API with google/gemini-2.0-flash-exp...")
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://web-bestfriendais-projects.vercel.app",
                "X-Title": "AvaxSearch",
            },
            model="google/gemini-2.0-flash-exp",
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Just say 'API working' if you can respond."
                }
            ]
        )
        
        response = completion.choices[0].message.content
        print(f"✅ OpenRouter API Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter API Error: {e}")
        return False

def test_langchain_integration():
    """Test LangChain integration."""
    try:
        # Set the API key in environment
        os.environ["BASIC_MODEL__API_KEY"] = "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"
        os.environ["BASIC_MODEL__BASE_URL"] = "https://openrouter.ai/api/v1"
        os.environ["BASIC_MODEL__MODEL"] = "google/gemini-2.0-flash-exp"
        
        print("🔍 Testing LangChain integration...")
        
        from src.llms.llm import get_llm_by_type
        from langchain_core.messages import HumanMessage
        
        llm = get_llm_by_type("basic")
        response = llm.invoke([HumanMessage(content="Hello! Just say 'LangChain working' if you can respond.")])
        
        print(f"✅ LangChain Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ LangChain Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenRouter Configuration")
    print("=" * 50)
    
    # Test direct API
    direct_ok = test_openrouter_direct()
    
    # Test LangChain integration
    langchain_ok = test_langchain_integration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Direct OpenRouter API: {'✅ PASS' if direct_ok else '❌ FAIL'}")
    print(f"  LangChain Integration: {'✅ PASS' if langchain_ok else '❌ FAIL'}")
    
    if direct_ok and langchain_ok:
        print("\n🎉 All tests passed! OpenRouter is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
