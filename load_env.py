"""
Simple utility to load environment variables from .env file
"""

import os


def load_env_file(filepath='.env'):
    """Load environment variables from a .env file"""
    if not os.path.exists(filepath):
        print(f"⚠️  Warning: {filepath} file not found")
        return False
    
    print(f"📄 Loading environment variables from {filepath}")
    loaded_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable
                os.environ[key] = value
                loaded_count += 1
                print(f"  ✓ Loaded: {key}")
    
    print(f"✅ Loaded {loaded_count} environment variables")
    return True


if __name__ == "__main__":
    load_env_file()
    
    # Show API key status
    api_key = os.getenv('API_KEY') or os.getenv('TOKENFACTORY_API_KEY') or os.getenv('TOKEN_FACTORY_API_KEY')
    if api_key:
        print(f"\n✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("\n⚠️  No API key found in environment")
