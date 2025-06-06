#!/usr/bin/env python3
"""
Test script to verify the Railway API is working correctly.
"""

import requests
import json
import time

BASE_URL = "https://dddd-production.up.railway.app"

def test_health():
    """Test the health endpoint."""
    print("🔍 Testing Railway Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_rag_config():
    """Test the RAG config endpoint."""
    print("\n🔍 Testing Railway RAG Config Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/rag/config")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ RAG config test failed: {e}")
        return False

def test_chat_stream():
    """Test the chat stream endpoint with a simple message."""
    print("\n🔍 Testing Railway Chat Stream Endpoint...")
    try:
        # Prepare the chat request
        chat_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Can you tell me what you are?"
                }
            ],
            "thread_id": "__default__",
            "resources": [],
            "max_plan_iterations": 1,
            "max_step_num": 2,
            "max_search_results": 2,
            "auto_accepted_plan": True,
            "interrupt_feedback": "",
            "mcp_settings": {},
            "enable_background_investigation": False
        }
        
        print("Sending chat request to Railway...")
        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            json=chat_request,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Railway chat stream started successfully!")
            print("📝 Response stream:")
            
            # Read the first few events from the stream
            event_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line and event_count < 10:  # Limit to first 10 events
                    print(f"  {line}")
                    event_count += 1
                elif event_count >= 10:
                    print("  ... (truncated)")
                    break
            
            return True
        else:
            print(f"❌ Railway chat stream failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Railway chat stream test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Railway AvaxSearch API")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health()
    
    # Test RAG config endpoint
    rag_ok = test_rag_config()
    
    # Test chat stream endpoint
    chat_ok = test_chat_stream()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Railway Test Results Summary:")
    print(f"  Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"  RAG Config: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    print(f"  Chat Stream: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    
    if all([health_ok, rag_ok, chat_ok]):
        print("\n🎉 All Railway tests passed! Your Railway deployment is working correctly.")
        return True
    else:
        print("\n⚠️  Some Railway tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
