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
        logging.FileHandler("chat_app.log", encoding="utf-8"),
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
        print("\n🤖 Bot : Thank you for rating me : ",rating)
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

# Define function schema for exit intent detection
exit_intent_function = {
    "name": "detect_exit_intent",
    "description": "Detect if the user wants to end the conversation",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "is_exit_intent": {
                "type": "BOOLEAN",
                "description": "Whether the message indicates the user wants to end the conversation"
            },
            "confidence": {
                "type": "NUMBER",
                "description": "Confidence level (0-1) that this is an exit intent"
            }
        },
        "required": ["is_exit_intent"]
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
                    "Pay attention when users provide feedback about the conversation in casual language. "
                    "Also detect when users want to end the conversation through phrases like 'bye', 'exit', "
                    "'end chat', 'quit', 'goodbye', 'leave', 'stop', or similar exit intents."
                ),
                tools=[feedback_function, exit_intent_function]
            )
            self.chat = self.model.start_chat(history=[])
            
            self.max_retries = 3
            logger.info(f"ChatBot initialized successfully with chat_id={self.chat_id}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            raise RuntimeError(f"Failed to initialize ChatBot: {e}")
    
    def detect_exit_intent(self, message: str) -> bool:
        """
        Check if the user message indicates they want to exit using the model
        
        Args:
            message: User's input message
            
        Returns:
            bool: True if exit intent detected, False otherwise
        """
        try:
            # Create a separate call to determine exit intent
            response = self.model.generate_content(
                f"Does this message indicate the user wants to end the conversation? Message: '{message}'",
                tools=[exit_intent_function],
                tool_choice={"function": "detect_exit_intent"}
            )
            
            # Check if there's a function call in the response
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call.name == "detect_exit_intent":
                        try:
                            args = json.loads(part.function_call.args)
                            if args.get("is_exit_intent", False):
                                return True
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.warning(f"Error parsing exit intent function call: {e}")
            
            return False
        
        except Exception as e:
            logger.error(f"Error detecting exit intent: {e}")

            
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
    
    def extract_feedback_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract feedback (review and rating) from user's response
        
        Args:
            response: User's feedback response
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with review and rating if detected,
                                     None otherwise
        """
        try:
            # First try to detect rating using pattern matching
            feedback_result = self.detect_feedback_in_message(response)
            
            if feedback_result:
                review, rating = feedback_result
                return {"review": review, "rating": rating}
            
            # If no rating was found but there's text, use it as review only
            if response.strip():
                return {"review": response, "rating": None}
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting feedback from response: {e}")
            return None
    
    def get_exit_feedback(self) -> Optional[Dict[str, Any]]:
        """
        Get feedback when user wants to exit
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary with review and rating if detected,
                                     None otherwise
        """
        try:
            # Ask for feedback directly without confirmation
            print("\n🤖 Bot : Before you go, I'd love to hear your thoughts about our conversation!")
            print("Please share your review and include a rating (1-5).")
            
            # Get feedback response
            feedback_response = input("\n😊 Your feedback: ").strip()
            
            # Skip if empty
            if not feedback_response:
                print("No problem! Have a great day!")
                return None
            
            # Try to extract feedback from the response
            feedback_data = self.extract_feedback_from_response(feedback_response)
            
            # If no rating was detected, ask specifically for a rating
            if feedback_data and feedback_data.get("rating") is None:
                try:
                    rating_input = input("Could you also rate our conversation from 1-5? ").strip()
                    if rating_input:
                        rating_value = int(rating_input)
                        if 1 <= rating_value <= 5:
                            feedback_data["rating"] = rating_value
                except ValueError:
                    print("No problem, we'll continue without a rating.")
            
            return feedback_data
            
        except KeyboardInterrupt:
            print("\nFeedback skipped.")
            return None
        except Exception as e:
            logger.error(f"Error getting exit feedback: {e}")
            print("Sorry, I couldn't process your feedback correctly.")
            return None
    
    def send_message(self, message: str) -> Tuple[str, Optional[Tuple[str, int]], bool]:
        """
        Send a message to the Gemini AI and get a response
        Also detect if the message contains feedback or exit intent
        
        Args:
            message: User's message
            
        Returns:
            Tuple[str, Optional[Tuple[str, int]], bool]: AI response, feedback tuple if detected, exit intent flag
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
                exit_intent_detected = False
                
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        # Check for feedback function call
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
                        
                        # Check for exit intent function call
                        elif hasattr(part, 'function_call') and part.function_call.name == "detect_exit_intent":
                            try:
                                args = json.loads(part.function_call.args)
                                if args.get("is_exit_intent", False):
                                    exit_intent_detected = True
                            except (json.JSONDecodeError, ValueError) as e:
                                logger.warning(f"Error parsing exit intent function call: {e}")
                
                # Prioritize local pattern matching over model detection for feedback
                final_feedback = feedback_result or feedback_from_model
                
                # If no exit intent was detected through function calling, check manually
                if not exit_intent_detected:
                    exit_intent_detected = self.detect_exit_intent(message)
                
                return response.text, final_feedback, exit_intent_detected
                
            except genai.types.generation_types.BlockedPromptException as e:
                logger.warning(f"Blocked prompt: {e}")
                return "I'm unable to respond to that request. Let's talk about something else.", None, False
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Connection error on attempt {attempt+1}/{self.max_retries}: {e}")
                if attempt == self.max_retries - 1:
                    return "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again later.", None, False
            except Exception as e:
                logger.error(f"Error on attempt {attempt+1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return "I'm having difficulty processing your request. Could you try rephrasing or asking something else?", None, False
        
        # Default fallback
        return "I couldn't process your request. Please try again.", None, False
    
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
                
                # Send message to Gemini and get response with potential feedback and exit intent
                bot_response, feedback_result, exit_intent = self.send_message(user_message)
                
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
                
                # Check for exit intent
                if exit_intent:
                    # Get feedback directly without confirmation
                    feedback = self.get_exit_feedback()
                    
                    if feedback:
                        if feedback.get("rating") is not None:
                            save_feedback(feedback["review"], feedback["rating"], self.chat_id)
                        else:
                            # Save feedback without rating
                            review = feedback.get("review", "Good conversation")
                            save_feedback(review, 0, self.chat_id)
                    
                    print("\n🤖 Bot : Thank you for chatting! Goodbye! 👋")
                    conversation_active = False
                    continue
                
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