#!/usr/bin/env python3
"""
DeerFlow Deployment Configuration Checker
This script helps verify that your deployment configuration is correct.
"""

import os
import sys
import json
import yaml
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def check_env_file(file_path):
    """Check environment file and list variables."""
    if not Path(file_path).exists():
        return False
    
    print(f"\n📋 Environment variables in {file_path}:")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0]
                print(f"   • {key}")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
    
    return True

def check_json_file(file_path):
    """Check if JSON file is valid."""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print(f"✅ {file_path} is valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {file_path} has invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_yaml_file(file_path):
    """Check if YAML file is valid."""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        print(f"✅ {file_path} is valid YAML")
        return True
    except yaml.YAMLError as e:
        print(f"❌ {file_path} has invalid YAML: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def main():
    print("🦌 DeerFlow Deployment Configuration Checker")
    print("=" * 50)
    
    # Check deployment configuration files
    print("\n🔧 Deployment Configuration Files:")
    config_files = [
        ("vercel.json", "Vercel configuration"),
        ("railway.toml", "Railway configuration"),
        (".env.production", "Backend production environment"),
        ("web/.env.production", "Frontend production environment"),
    ]
    
    all_config_present = True
    for file_path, description in config_files:
        if not check_file_exists(file_path, description):
            all_config_present = False
    
    # Check JSON files
    print("\n📄 JSON Configuration Validation:")
    if Path("vercel.json").exists():
        check_json_file("vercel.json")
    
    if Path("web/package.json").exists():
        check_json_file("web/package.json")
    
    # Check YAML files
    print("\n📄 YAML Configuration Validation:")
    if Path("conf.yaml").exists():
        check_yaml_file("conf.yaml")
    
    # Check environment files
    print("\n🔐 Environment Configuration:")
    env_files = [
        ".env",
        ".env.production", 
        "web/.env.production"
    ]
    
    for env_file in env_files:
        if Path(env_file).exists():
            check_env_file(env_file)
    
    # Check required directories
    print("\n📁 Required Directories:")
    directories = [
        ("web", "Frontend directory"),
        ("src", "Backend source directory"),
        ("web/src", "Frontend source directory"),
    ]
    
    for dir_path, description in directories:
        check_file_exists(dir_path, description)
    
    # Summary
    print("\n" + "=" * 50)
    if all_config_present:
        print("✅ All deployment configuration files are present!")
        print("\n🚀 Next steps:")
        print("1. Configure environment variables in Railway and Vercel")
        print("2. Deploy backend to Railway")
        print("3. Deploy frontend to Vercel")
        print("4. Update CORS configuration")
        print("\nSee DEPLOYMENT.md for detailed instructions.")
    else:
        print("❌ Some configuration files are missing.")
        print("Run the deployment setup first or check DEPLOYMENT.md")
    
    print("\n📖 For help, see:")
    print("   • DEPLOYMENT.md - Detailed deployment guide")
    print("   • VERCEL_DEPLOYMENT.md - Quick start guide")

if __name__ == "__main__":
    main()
