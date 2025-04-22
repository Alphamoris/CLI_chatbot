#!/usr/bin/env python3
"""
Test script for the Gemini CLI Chat Bot.
This script tests the basic functionality of the ChatBot class.
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_chat.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_chat")

# Mock the API key for testing
os.environ['GEMINI_API_KEY'] = 'fake_api_key_for_testing'

# Import the environment manager
from env_manager import setup_environment, create_env_example

class TestChatBot(unittest.TestCase):
    """Test cases for the ChatBot class."""
    
    def setUp(self):
        """Set up for the tests"""
        # Make sure data directory exists
        os.makedirs("data", exist_ok=True)
    
    def test_environment_setup(self):
        """Test that environment setup works correctly with our mock key."""
        self.assertTrue(setup_environment())
    
    @patch('google.generativeai.GenerativeModel')
    def test_exit_detection(self, mock_model):
        """Test the exit detection functionality."""
        # Mock the GenerativeModel to avoid API calls
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        mock_instance.start_chat.return_value = MagicMock()
        
        # Now we can import the ChatBot
        from src.chat_app import ChatBot
        
        chatbot = ChatBot()
        
        # Test exit phrases
        exit_phrases = [
            "bye", "exit", "end chat", "quit", "goodbye", 
            "i want to leave", "stop", "end", "close"
        ]
        for phrase in exit_phrases:
            with self.subTest(phrase=phrase):
                self.assertTrue(
                    chatbot.detect_exit_intent(phrase),
                    f"Failed to detect exit intent in '{phrase}'"
                )
        
        # Test non-exit phrases
        non_exit_phrases = [
            "hello", "how are you?", "tell me a joke",
            "what's the weather", "thanks for the help"
        ]
        for phrase in non_exit_phrases:
            with self.subTest(phrase=phrase):
                self.assertFalse(
                    chatbot.detect_exit_intent(phrase),
                    f"Incorrectly detected exit intent in '{phrase}'"
                )
    
    @patch('google.generativeai.GenerativeModel')
    def test_chat_initialization(self, mock_model):
        """Test that the chat bot initializes properly."""
        # Mock the model
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        mock_instance.start_chat.return_value = MagicMock()
        
        # Import and initialize ChatBot
        from src.chat_app import ChatBot
        
        try:
            chatbot = ChatBot()
            self.assertIsNotNone(chatbot)
            self.assertIsNotNone(chatbot.model)
            self.assertIsNotNone(chatbot.chat)
        except Exception as e:
            self.fail(f"ChatBot initialization failed with error: {e}")

def print_manual_test_results():
    """Print a simple manual test for visual verification."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Manual Test Results{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Check environment variables
    print(f"• GEMINI_API_KEY is set: {Fore.GREEN if os.getenv('GEMINI_API_KEY') else Fore.RED}{'✓' if os.getenv('GEMINI_API_KEY') else '✗'}{Style.RESET_ALL}")
    
    # Check data directory
    data_dir_exists = os.path.isdir("data")
    print(f"• Data directory exists: {Fore.GREEN if data_dir_exists else Fore.RED}{'✓' if data_dir_exists else '✗'}{Style.RESET_ALL}")
    if not data_dir_exists:
        os.makedirs("data", exist_ok=True)
        print(f"  {Fore.YELLOW}Created data directory{Style.RESET_ALL}")
    
    # Test exit phrases
    try:
        exit_phrases = ["bye", "exit", "end chat", "quit", "goodbye"]
        print(f"\n{Fore.CYAN}Testing exit detection...{Style.RESET_ALL}")
        
        # Import with mocking to avoid actual API calls
        with patch('google.generativeai.GenerativeModel'):
            from src.chat_app import ChatBot
            chatbot = ChatBot()
            
            for phrase in exit_phrases:
                result = chatbot.detect_exit_intent(phrase)
                print(f"  Phrase '{phrase}': {Fore.GREEN if result else Fore.RED}{'✓' if result else '✗'}{Style.RESET_ALL}")
            
            # Test a non-exit phrase
            non_exit = "hello"
            result = chatbot.detect_exit_intent(non_exit)
            print(f"  Phrase '{non_exit}' (should not exit): {Fore.GREEN if not result else Fore.RED}{'✓' if not result else '✗'}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error during testing: {e}{Style.RESET_ALL}")

def main():
    """Run the test suite."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Gemini CLI Chat - Test Suite{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run all tests and capture results
    try:
        # Run the unittest tests
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    except Exception as e:
        print(f"\n{Fore.RED}Error running unittest: {e}{Style.RESET_ALL}")
    
    # Run the manual tests
    print_manual_test_results()

if __name__ == "__main__":
    main() 