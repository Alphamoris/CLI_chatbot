"""
Environment Manager
Utility for handling environment variables and API keys
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("env_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("env_manager")

def setup_environment():
    """
    Load environment variables and check for required API keys.
    Returns True if all required variables are present, otherwise guides the user and exits.
    """
    # Create example file first
    create_env_example()
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning(".env file not found")
        show_env_setup_instructions()
        return False
    
    # Load from .env file if it exists
    load_dotenv()
    
    # Check if Gemini API key exists and is valid
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY environment variable is empty or not found")
        show_env_setup_instructions()
        return False
    
    # Check if the API key looks suspicious (like the default placeholder value)
    if gemini_api_key == "your_gemini_api_key_here":
        logger.error("GEMINI_API_KEY contains the placeholder value")
        print("\n" + "="*50)
        print("⚠️ INVALID API KEY DETECTED ⚠️")
        print("="*50)
        print("\nYour .env file contains the placeholder API key.")
        print("Please replace it with your actual Gemini API key.")
        print("\nGEMINI_API_KEY=your_actual_api_key_here\n")
        print("="*50)
        return False
    
    # Check if API key has proper format (basic check)
    if not gemini_api_key.startswith("AI") and len(gemini_api_key) < 20:
        logger.warning(f"GEMINI_API_KEY format looks suspicious: {gemini_api_key[:5]}...")
        print("\n" + "="*50)
        print("⚠️ API KEY FORMAT WARNING ⚠️")
        print("="*50)
        print("\nYour API key doesn't match the expected format.")
        print("Gemini API keys typically start with 'AI' and are quite long.")
        print("The application will continue, but might fail when connecting to the API.")
        print("="*50)
        # Continue anyway - the API will validate it
    
    return True

def show_env_setup_instructions():
    """Show detailed instructions for setting up the .env file"""
    print("\n" + "="*50)
    print("🔑 API KEY NOT FOUND 🔑")
    print("="*50)
    print("\nTo use this application, you need a Gemini API key.")
    print("\nFollow these steps:")
    print("1. Visit https://aistudio.google.com/app/apikey")
    print("2. Create or sign in to your Google account")
    print("3. Create a new API key")
    print("4. Create a file named '.env' in this directory with the content:")
    print("\nGEMINI_API_KEY=your_api_key_here\n")
    
    # Check if .env.example exists and show it as a reference
    if os.path.exists('.env.example'):
        print("You can use the .env.example file as a template:")
        print("  - Copy .env.example to .env")
        print("  - Replace the placeholder with your actual API key")
        
        # Show platform-specific copy commands
        if sys.platform == 'win32':
            print("\nOn Windows:")
            print("  copy .env.example .env")
        else:
            print("\nOn macOS/Linux:")
            print("  cp .env.example .env")
    
    print("="*50)

def create_env_example():
    """Create an example .env file if it doesn't exist"""
    example_file = '.env.example'
    if not os.path.exists(example_file):
        try:
            with open(example_file, 'w') as f:
                f.write("# Gemini API Key\n")
                f.write("# Get your free API key from: https://aistudio.google.com/app/apikey\n")
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            logger.info(f"Created {example_file}")
        except Exception as e:
            logger.error(f"Could not create {example_file}: {e}")
            print(f"Warning: Could not create {example_file}: {e}")
    
    # Also try to create an actual .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        try:
            with open(env_file, 'w') as f:
                f.write("# Gemini API Key\n")
                f.write("# Get your free API key from: https://aistudio.google.com/app/apikey\n")
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            logger.info(f"Created {env_file}")
            print(f"Created {env_file} - Please edit this file to add your API key")
        except Exception as e:
            logger.error(f"Could not create {env_file}: {e}")

def validate_api_key(api_key):
    """Perform basic validation on the API key format"""
    if not api_key or len(api_key) < 10:
        return False
    return True

if __name__ == "__main__":
    # If run directly, this will check for the API key and provide instructions
    if setup_environment():
        print("✅ Environment is set up correctly!")
        print("You can run the chat application with: python cli_chat.py")
    else:
        sys.exit(1) 