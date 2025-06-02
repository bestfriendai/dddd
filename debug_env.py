#!/usr/bin/env python3
"""
Debug script to check environment variables and configuration loading.
"""

import os
import sys
from pathlib import Path

def check_environment_variables():
    """Check if the required environment variables are set."""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    # Check for LLM configuration environment variables
    llm_types = ["BASIC", "REASONING", "VISION"]
    required_keys = ["API_KEY", "BASE_URL", "MODEL"]
    
    found_vars = {}
    for llm_type in llm_types:
        print(f"\n📋 {llm_type}_MODEL configuration:")
        type_vars = {}
        for key in required_keys:
            env_var = f"{llm_type}_MODEL__{key}"
            value = os.getenv(env_var)
            if value:
                print(f"  ✅ {env_var}: {value[:20]}...")
                type_vars[key.lower()] = value
            else:
                print(f"  ❌ {env_var}: Not set")
        found_vars[llm_type.lower()] = type_vars
    
    return found_vars

def check_config_file():
    """Check if the configuration file exists and can be loaded."""
    print("\n🔍 Checking Configuration File...")
    print("=" * 50)
    
    conf_path = Path(__file__).parent / "conf.yaml"
    print(f"Config file path: {conf_path}")
    print(f"Config file exists: {conf_path.exists()}")
    
    if conf_path.exists():
        try:
            with open(conf_path, 'r') as f:
                content = f.read()
            print(f"Config file size: {len(content)} bytes")
            print("Config file content preview:")
            print("-" * 30)
            print(content[:500])
            if len(content) > 500:
                print("...")
            print("-" * 30)
            return True
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return False
    else:
        print("❌ Config file not found")
        return False

def test_llm_creation():
    """Test creating an LLM instance."""
    print("\n🔍 Testing LLM Creation...")
    print("=" * 50)
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.llms.llm import _get_env_llm_conf
        
        # Test environment variable parsing
        env_conf = _get_env_llm_conf("basic")
        print(f"Environment config for 'basic': {env_conf}")
        
        if env_conf:
            print("✅ Environment variables found for basic LLM")
            required_keys = ["api_key", "model"]
            for key in required_keys:
                if key in env_conf:
                    print(f"  ✅ {key}: {env_conf[key][:20]}...")
                else:
                    print(f"  ❌ {key}: Missing")
        else:
            print("❌ No environment variables found for basic LLM")
        
        return len(env_conf) > 0
        
    except Exception as e:
        print(f"❌ Error testing LLM creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all checks."""
    print("🚀 DeerFlow LLM Configuration Debug")
    print("=" * 60)
    
    # Run checks
    env_vars = check_environment_variables()
    config_file = check_config_file()
    llm_creation = test_llm_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  Environment Variables: {'✅' if any(env_vars.values()) else '❌'}")
    print(f"  Configuration File: {'✅' if config_file else '❌'}")
    print(f"  LLM Creation Test: {'✅' if llm_creation else '❌'}")
    
    if any(env_vars.values()) or config_file:
        print("\n🎉 At least one configuration method is available!")
    else:
        print("\n⚠️  No configuration found. Please check your setup.")
    
    return any(env_vars.values()) or config_file

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
