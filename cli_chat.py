#!/usr/bin/env python3
"""
CLI Chat Bot using Google's Gemini API
This script runs a command-line chat interface powered by Gemini AI.
"""

import os
import sys
import logging
import traceback
import platform
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cli_chat.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cli_chat")

def print_banner():
    """Print a colorful welcome banner"""
    print(f"\n{Fore.CYAN}{'='*100}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}                                    🤖 GEMINI CLI CHAT BOT 🤖{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*100}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}      • Interactive chat powered by Google's Gemini AI{Style.RESET_ALL}")
    print(f"{Fore.GREEN}      • Smart and helpful CLI assistant{Style.RESET_ALL}")
    print(f"{Fore.GREEN}      • Exit intent detection implemented bot{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*100}{Style.RESET_ALL}\n")


def check_dependencies():
    """Verify that all required dependencies are installed"""
    try:
        import google.generativeai
        import dotenv
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        print(f"\n{Fore.RED}Error: Missing dependencies.{Style.RESET_ALL}")
        print("Please install required packages with:")
        print(f"{Fore.YELLOW}pip install -r requirements.txt{Style.RESET_ALL}\n")
        return False

def main():
    """Main entry point for the CLI Chat application."""
    try:
        print_banner()
        
        # Check dependencies first
        if not check_dependencies():
            sys.exit(1)
        
        # Import our environment manager
        from env_manager import setup_environment, create_env_example
        
        # Create example .env file for reference
        create_env_example()
        
        # Check if we have the necessary environment variables
        if not setup_environment():
            logger.error("Environment setup failed")
            sys.exit(1)
        
        try:
            from src.chat_app import ChatBot
        except ImportError as e:
            logger.error(f"Could not import ChatBot: {e}")
            print(f"\n{Fore.RED}Error: Could not import ChatBot.{Style.RESET_ALL}")
            print("Make sure the src directory exists and contains chat_app.py.")
            print(f"Details: {e}")
            sys.exit(1)
        
        try:
            print(f"\n{Fore.YELLOW}Initializing Gemini chat...{Style.RESET_ALL}")
            chatbot = ChatBot()
            chatbot.run()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Chat ended by user. Goodbye!{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Error in chat session: {e}")
            print(f"\n{Fore.RED}Error running the chat application: {e}{Style.RESET_ALL}")
            
            # Offer some troubleshooting advice based on the error
            if "API key" in str(e).lower() or "authentication" in str(e).lower():
                print("\nThis looks like an API key issue. Please check:")
                print("1. Your .env file contains a valid Gemini API key")
                print("2. The API key is correctly formatted (no quotes or spaces)")
                print("3. Your API key has not expired or been revoked")
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                print("\nThis looks like a network issue. Please check:")
                print("1. Your internet connection is working")
                print("2. Any firewall or proxy settings that might block the connection")
            else:
                # Show debug info for developers
                print(f"\n{Fore.YELLOW}Debug information:{Style.RESET_ALL}")
                
                # Ask if the user wants to see the full error traceback
                print("Would you like to see the full error traceback? (y/n)")
                if input("> ").lower().strip() in ('y', 'yes'):
                    print(f"\n{Fore.RED}Error traceback:{Style.RESET_ALL}")
                    traceback.print_exc()
            
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        print(f"\n{Fore.RED}Critical error: {e}{Style.RESET_ALL}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 