#!/usr/bin/env python3
"""
Test script to verify LLM configuration is working correctly.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """Test that the configuration file can be loaded."""
    try:
        from src.config.loader import load_yaml_config
        conf_path = project_root / "conf.yaml"
        conf = load_yaml_config(str(conf_path))
        
        print("✅ Configuration file loaded successfully")
        print(f"Available config keys: {list(conf.keys())}")
        
        # Check if required models are present
        required_models = ["BASIC_MODEL", "REASONING_MODEL", "VISION_MODEL"]
        for model in required_models:
            if model in conf:
                print(f"✅ {model} configuration found")
                model_conf = conf[model]
                if isinstance(model_conf, dict):
                    print(f"   - api_key: {'✅' if 'api_key' in model_conf else '❌'}")
                    print(f"   - model: {'✅' if 'model' in model_conf else '❌'}")
                    print(f"   - base_url: {'✅' if 'base_url' in model_conf else '❌'}")
            else:
                print(f"❌ {model} configuration missing")
        
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def test_llm_creation():
    """Test that LLM instances can be created."""
    try:
        from src.llms.llm import get_llm_by_type
        
        # Test basic LLM (used by coordinator)
        basic_llm = get_llm_by_type("basic")
        print("✅ Basic LLM created successfully")
        print(f"   - Model: {getattr(basic_llm, 'model_name', 'Unknown')}")
        print(f"   - Base URL: {getattr(basic_llm, 'openai_api_base', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_mapping():
    """Test that agent LLM mapping is correct."""
    try:
        from src.config.agents import AGENT_LLM_MAP
        
        print("✅ Agent LLM mapping loaded successfully")
        for agent, llm_type in AGENT_LLM_MAP.items():
            print(f"   - {agent}: {llm_type}")
        
        # Check coordinator specifically
        if "coordinator" in AGENT_LLM_MAP:
            coordinator_llm_type = AGENT_LLM_MAP["coordinator"]
            print(f"✅ Coordinator uses LLM type: {coordinator_llm_type}")
        else:
            print("❌ Coordinator not found in agent mapping")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error loading agent mapping: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing LLM Configuration...")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("LLM Creation", test_llm_creation),
        ("Agent Mapping", test_agent_mapping),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! LLM configuration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
