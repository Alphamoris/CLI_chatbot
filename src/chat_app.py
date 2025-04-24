import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chat_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chat_bot")

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY environment variable not found")
        print("Error: GEMINI_API_KEY not set. Please check your .env file.")
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    sys.exit(1)

def create_directory_if_not_exists(dir_name: str) -> None:
    """Create a directory if it doesn't exist"""
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"Created directory: {dir_name}")
    except Exception as e:
        logger.error(f"Error creating directory {dir_name}: {e}")

# Create data directory for storing feedback and chat history
create_directory_if_not_exists("data")

def save_feedback(review: str, rating: int, chat_id: str = None) -> bool:
    """
    Save user feedback to a file
    
    Args:
        review: User's review text
        rating: Rating from 1-5
        chat_id: Optional identifier to link feedback to chat session
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        with open("data/feedback.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}]\n")
            if chat_id:
                f.write(f"Chat ID: {chat_id}\n")
            f.write(f"Rating: {rating}/5\n")
            f.write(f"Review: {review}\n")
            f.write("-" * 50 + "\n")
        logger.info(f"Feedback saved: rating={rating}")
        return True
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        print(f"Error saving feedback: {e}")
        return False

def save_chat_history(user_message: str, bot_response: str, chat_id: str) -> bool:
    """
    Save chat history to a file
    
    Args:
        user_message: Message from the user
        bot_response: Response from the bot
        chat_id: Identifier for the chat session
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        with open(f"data/chat_history_{chat_id}.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}]\n")
            f.write(f"User: {user_message}\n")
            f.write(f"Bot: {bot_response}\n")
            f.write("-" * 50 + "\n")
        logger.debug("Chat history saved")
        return True
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")
        return False

# Define function schema for the feedback collection
# The correct format for function calling with the latest Gemini API
feedback_function = {
    "name": "collect_feedback",
    "description": "Collect user feedback and rating from natural conversation",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "review": {
                "type": "STRING",
                "description": "User's review of the chat experience extracted from natural conversation"
            },
            "rating": {
                "type": "NUMBER",
                "description": "Rating from 1 to 5, where 5 is the best, extracted from natural conversation"
            },
            "is_feedback": {
                "type": "BOOLEAN",
                "description": "Whether this message contains feedback about the chat experience"
            }
        },
        "required": ["is_feedback"]
    }
}

class ChatBot:
    """Main ChatBot class for handling Gemini AI interactions"""
    
    def __init__(self, model_name: str = "gemini-1.5-pro", temperature: float = 0.7):
        """
        Initialize the ChatBot with Gemini API
        
        Args:
            model_name: Name of the Gemini model to use
            temperature: Temperature parameter for text generation (0.0-1.0)
        """
        try:
            logger.info(f"Initializing ChatBot with {model_name}")
            
            # Generate a unique chat ID for this session
            self.chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Initialize model with function calling capability
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                },
                system_instruction=(
                    "You are a helpful AI assistant. Be concise, friendly, and precise in your answers. "
                    "If you don't know something, say so rather than making up information. "
                    "Pay attention when users provide feedback about the conversation in casual language."
                ),
                tools=[feedback_function]
            )
            self.chat = self.model.start_chat(history=[])
            
            self.exit_phrases = [
                "bye", "exit", "end chat", "quit", "goodbye", 
                "leave", "i want to leave", "stop", "end", "close"
            ]
            self.max_retries = 3
            logger.info(f"ChatBot initialized successfully with chat_id={self.chat_id}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            raise RuntimeError(f"Failed to initialize ChatBot: {e}")
    
    def detect_exit_intent(self, message: str) -> bool:
        """
        Check if the user message indicates they want to exit
        
        Args:
            message: User's input message
            
        Returns:
            bool: True if exit intent detected, False otherwise
        """
        return any(phrase in message.lower() for phrase in self.exit_phrases)
    
    def detect_feedback_in_message(self, message: str) -> Optional[Tuple[str, int]]:
        """
        Detect if a user message contains feedback and rating using local pattern matching
        
        Args:
            message: User's input message
            
        Returns:
            Optional[Tuple[str, int]]: Tuple of (review, rating) if detected, None otherwise
        """
        try:
            # Enhanced pattern matching to capture more natural conversation
            rating_patterns = [
                r'(?:rating|rate|score|give)[^\d]*?(\d+)',    # "rating of 4" or "rate it 4"
                r'(\d+)(?:\s*\/\s*5)',                        # "4/5"
                r'(\d+)(?:\s*out of\s*5)',                    # "4 out of 5"
                r'(\d+)(?:\s*stars)',                         # "4 stars"
                r'(?:thumbs|thumb) up (\d+)',                 # "thumbs up 4"
                r'(\d+) (?:points?)',                         # "4 points"
                r'would (?:give|rate).*?(\d+)',               # "would give rating of 4"
                r'I(?:\'d)? give (?:it |this |you )?(?:a )?(\d+)', # "I'd give it a 4"
                r'(?:rated|rating) (?:it |this |you )?(?:a )?(\d+)', # "rated it a 4"
                r'(\d+) for (?:this|the) (?:chat|conversation)'      # "4 for this chat"
            ]
            
            for pattern in rating_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        # Use the whole message as the review
                        return message, rating
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting feedback in message: {e}")
            return None
    
    def get_feedback(self) -> Optional[Dict[str, Any]]:
        """
        Get feedback from the user
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary with review and rating if successful,
                                     None otherwise
        """
        try:
            # Display the feedback request to the user directly
            print("\nBefore you go, I'd love to hear your thoughts about our conversation!")
            
            # Get review
            review = input("Your review (press Enter to skip): ").strip()
            
            # If user skips review, ask if they're sure
            if not review:
                skip_confirm = input("Are you sure you want to skip leaving feedback? (y/n): ").strip().lower()
                if skip_confirm.startswith('y'):
                    print("No problem! Have a great day!")
                    return None
                review = input("Your review: ").strip()
                while not review:
                    review = input("Please enter a review, or type 'skip' to exit: ").strip()
                    if review.lower() == 'skip':
                        return None
            
            # Get and validate rating
            rating = None
            attempts = 0
            max_attempts = 3
            
            while rating is None and attempts < max_attempts:
                try:
                    attempts += 1
                    rating_input = input("Your rating (1-5) or press Enter to skip: ").strip()
                    if not rating_input:
                        skip_confirm = input("Skip rating? (y/n): ").strip().lower()
                        if skip_confirm.startswith('y'):
                            print("Thanks for your review!")
                            # Return just the review without a rating
                            return {"review": review, "rating": None}
                    else:
                        rating_value = int(rating_input)
                        if 1 <= rating_value <= 5:
                            rating = rating_value
                        else:
                            print("Please enter a number between 1 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\nFeedback skipped.")
                    return None
            
            # If we've exceeded attempts but still don't have a valid rating
            if rating is None:
                print("We'll continue without a rating.")
                return {"review": review, "rating": None}
            
            # Create structured feedback data
            feedback_data = {
                "review": review,
                "rating": rating
            }
            
            return feedback_data
            
        except KeyboardInterrupt:
            print("\nFeedback skipped.")
            return None
        except Exception as e:
            logger.error(f"Error getting feedback: {e}")
            print("Sorry, I couldn't process your feedback correctly.")
            return None
    
    def send_message(self, message: str) -> Tuple[str, Optional[Tuple[str, int]]]:
        """
        Send a message to the Gemini AI and get a response
        Also detect if the message contains feedback
        
        Args:
            message: User's message
            
        Returns:
            Tuple[str, Optional[Tuple[str, int]]]: AI response and feedback tuple if detected
        """
        for attempt in range(self.max_retries):
            try:
                # First check for feedback with local pattern matching
                feedback_result = self.detect_feedback_in_message(message)
                
                # Send the message to Gemini
                response = self.chat.send_message(
                    message
                )
                
                # Check if Gemini detected feedback via function calling
                feedback_from_model = None
                
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call.name == "collect_feedback":
                            try:
                                args = json.loads(part.function_call.args)
                                if args.get("is_feedback", False):
                                    rating = args.get("rating")
                                    review = args.get("review", message)
                                    if rating and 1 <= int(float(rating)) <= 5:
                                        feedback_from_model = (review, int(float(rating)))
                            except (json.JSONDecodeError, ValueError) as e:
                                logger.warning(f"Error parsing function call args: {e}")
                
                # Prioritize local pattern matching over model detection
                final_feedback = feedback_result or feedback_from_model
                
                return response.text, final_feedback
                
            except genai.types.generation_types.BlockedPromptException as e:
                logger.warning(f"Blocked prompt: {e}")
                return "I'm unable to respond to that request. Let's talk about something else.", None
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Connection error on attempt {attempt+1}/{self.max_retries}: {e}")
                if attempt == self.max_retries - 1:
                    return "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again later.", None
            except Exception as e:
                logger.error(f"Error on attempt {attempt+1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return "I'm having difficulty processing your request. Could you try rephrasing or asking something else?", None
        
        # Default fallback
        return "I couldn't process your request. Please try again.", None
    
    def confirm_exit(self) -> bool:
        """
        Confirm if the user really wants to exit
        
        Returns:
            bool: True if the user confirms exit, False otherwise
        """
        try:
            confirmation = input("\nDo you want to end this conversation? (y/n): ").strip().lower()
            return confirmation.startswith('y')
        except KeyboardInterrupt:
            return True
        except Exception:
            return False
    
    def run(self):
        """Run the chatbot conversation loop"""
        print("\n🤖 Welcome to the Chat Bot! Type 'exit' when you're done.\n")
        conversation_active = True
        
        while conversation_active:
            try:
                # Get user input
                user_message = input("\n😊 You: ").strip()
                
                # Skip empty messages
                if not user_message:
                    continue
                
                # Check for exit intent
                if self.detect_exit_intent(user_message):
                    # if self.confirm_exit():
                    #     feedback = self.get_feedback()
                        
                    #     if feedback and feedback.get("rating") is not None:
                    #         save_feedback(feedback["review"], feedback["rating"], self.chat_id)
                    #         print("\nThank you for your feedback!")
                        
                    print("\nThank you for chatting! Goodbye! 👋")
                    #     conversation_active = False
                    #     continue
                    else:
                        print("Great! Let's continue our conversation.")
                        continue
                
                # Send message to Gemini and get response with potential feedback
                bot_response, feedback_result = self.send_message(user_message)
                
                # If feedback was detected, save it and acknowledge
                if feedback_result:
                    review, rating = feedback_result
                    save_feedback(review, rating, self.chat_id)
                    feedback_ack = f"Thanks for your rating of {rating}/5! I've saved your feedback. "
                    bot_response = feedback_ack + bot_response
                
                # Display the response
                print(f"\n🤖 Bot: {bot_response}")
                
                # Save chat history
                save_chat_history(user_message, bot_response, self.chat_id)
                
            except KeyboardInterrupt:
                logger.info("Chat ended by KeyboardInterrupt")
                print("\n\nChat ended by user. Goodbye! 👋")
                conversation_active = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"\nAn error occurred: {e}")
                print("Let's continue our conversation.")

if __name__ == "__main__":
    try:
        print("Starting Chat Bot...")
        chatbot = ChatBot()
        chatbot.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)