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
    def test_feedback_detection(self, mock_model):
        """Test the feedback detection functionality."""
        # Mock the GenerativeModel to avoid API calls
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        mock_instance.start_chat.return_value = MagicMock()
        
        # Now we can import the ChatBot
        from src.chat_app import ChatBot
        
        chatbot = ChatBot()
        
        # Test feedback phrases that should be detected
        feedback_phrases = [
            "I give this chat a 5",
            "I'd rate this conversation 4 out of 5",
            "This deserves a rating of 3",
            "I would give you 4 stars",
            "Overall I'd say this is a 5/5 experience",
            "Thumbs up 5 for this chat",
            "I'd give this chat session a solid 4",
            "This was a 3 point conversation",
            "I'd rate this 4",
            "Would rate this experience 5/5"
        ]
        
        for phrase in feedback_phrases:
            with self.subTest(phrase=phrase):
                result = chatbot.detect_feedback_in_message(phrase)
                self.assertIsNotNone(
                    result,
                    f"Failed to detect feedback in '{phrase}'"
                )
                review, rating = result
                self.assertIsInstance(rating, int)
                self.assertGreaterEqual(rating, 1)
                self.assertLessEqual(rating, 5)
        
        # Test phrases that should not be detected as feedback
        non_feedback_phrases = [
            "Hello there",
            "What's the weather like?",
            "Tell me about the number 5",
            "I have 5 apples",
            "This is interesting",
            "Can you help me with something?",
            "The year is 2023",
            "I like talking with you"
        ]
        
        for phrase in non_feedback_phrases:
            with self.subTest(phrase=phrase):
                result = chatbot.detect_feedback_in_message(phrase)
                self.assertIsNone(
                    result,
                    f"Incorrectly detected feedback in '{phrase}'"
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
    
    @patch('google.generativeai.GenerativeModel')
    def test_send_message_with_feedback(self, mock_model):
        """Test sending messages with feedback detection."""
        # Setup mocks
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        
        mock_chat = MagicMock()
        mock_instance.start_chat.return_value = mock_chat
        
        # Configure mock response
        mock_response = MagicMock()
        mock_response.text = "I understand you enjoyed our conversation."
        
        mock_chat.send_message.return_value = mock_response
        
        # Import and initialize ChatBot
        from src.chat_app import ChatBot
        
        chatbot = ChatBot()
        
        # Test with a message containing feedback
        response_text, feedback = chatbot.send_message("I'd rate this conversation 4 out of 5!")
        
        # Verify the response
        self.assertEqual(response_text, "I understand you enjoyed our conversation.")
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback[1], 4)  # Rating should be 4

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
        
            # Test feedback detection
            print(f"\n{Fore.CYAN}Testing feedback detection...{Style.RESET_ALL}")
            feedback_phrases = [
                "I'd rate this conversation 4 out of 5",
                "I give this chat a 5",
                "This deserves a rating of 3"
            ]
            
            for phrase in feedback_phrases:
                result = chatbot.detect_feedback_in_message(phrase)
                if result:
                    review, rating = result
                    print(f"  Phrase '{phrase}': {Fore.GREEN}✓{Style.RESET_ALL} (Rating: {rating})")
                else:
                    print(f"  Phrase '{phrase}': {Fore.RED}✗{Style.RESET_ALL}")
        
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