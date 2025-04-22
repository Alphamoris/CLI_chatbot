# 🤖 CLI-based Chat Application using Gemini API

<div align="center">

![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

A powerful command-line chat application that lets you interact with Google's state-of-the-art Gemini AI language model. This application provides an intuitive interface for natural conversations with an AI assistant right in your terminal.

[Watch the video](https://drive.google.com/file/d/1g2boXnZLzcX1HwLo0E7O45On-CrVuEg_/view?usp=sharing)

<div align="center">


</div>

## ✨ Features

- 🗣️ **Interactive Chat Interface** - Natural conversation with Google's Gemini AI
- 🔍 **Smart Exit Detection** - Automatically detects when you want to end the chat
- 📊 **Feedback Collection** - Gathers reviews and ratings when you exit
- 💾 **Conversation History** - Saves your chat sessions for future reference
- 🎨 **Colorful Interface** - Easy-to-read, aesthetically pleasing terminal output
- 🛡️ **Robust Error Handling** - Detailed error messages and recovery options
- 📝 **Comprehensive Logging** - Helps troubleshoot any issues

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A free Gemini API key

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/gemini-cli-chat.git
cd gemini-cli-chat
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Get a Gemini API Key**

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get your free API key.

4. **Configure your API Key**

```bash
# On Windows
copy .env.example .env

# On macOS/Linux
cp .env.example .env
```

Then edit the `.env` file to add your API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### 🎮 Running the Application

Simply execute:

```bash
python cli_chat.py
```

## 💬 Example Chat Session

```
=============================================================
                 GEMINI CLI CHAT BOT
=============================================================
• Interactive chat powered by Google's Gemini AI
• Smart and helpful CLI assistant
• Exit intent detection implemented bot
=============================================================

Initializing Gemini chat...

😊 You: Hello, who are you?

🤖 Bot: I'm an AI assistant powered by Google's Gemini model. I'm here to help answer questions, provide information, or just chat. How can I assist you today?

😊 You: What can you do?

🤖 Bot: I can help with a variety of tasks including:
- Answering general knowledge questions
- Providing explanations on various topics
- Giving recommendations
- Creative writing assistance
- Problem-solving and brainstorming
- General conversation

Is there something specific you'd like help with?

😊 You: bye

I've enjoyed our conversation! Before you go, I'd appreciate your feedback.

Your review: The bot responses were very helpful and natural.
Your rating (1-5): 5

Thank you for your feedback!

Thank you for chatting! Goodbye! 👋
```

## 📁 Project Structure

```
gemini-cli-chat/
├── cli_chat.py          # Main entry script
├── src/
│   └── chat_app.py      # Core chatbot implementation
├── data/                # Created automatically
│   ├── feedback.txt     # Saved user feedback
│   └── chat_history.txt # Saved chat conversations
├── env_manager.py       # Environment variable management
├── test_chat.py         # Test script for verification
├── requirements.txt     # Python dependencies
├── .env                 # API key configuration (create this)
├── .env.example         # Example environment file
├── README.md            # This documentation
└── LICENSE              # MIT License
```

## 🧪 Testing

To run tests and verify your setup:

```bash
python test_chat.py
```

This verifies:
- Exit phrase detection
- Environment setup
- Basic functionality

## 📋 Detailed Instructions

### Setting Up Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Create or edit the `.env` file in the project root
6. Add your key: `GEMINI_API_KEY=your_api_key_here`

### Common Issues and Solutions

#### API Key Problems

- **Error**: "API key not found" or authentication errors
- **Solution**: Ensure your `.env` file exists and contains a valid API key

#### Network Issues

- **Error**: Connection timeouts or API unreachable
- **Solution**: Check your internet connection and any firewall settings

#### Missing Dependencies

- **Error**: ImportError for certain modules
- **Solution**: Run `pip install -r requirements.txt` again

## 🔧 Advanced Configuration

You can modify these parameters in `src/chat_app.py`:

- **Model**: Change `model_name` in the ChatBot constructor
- **Temperature**: Adjust creativity level (0.0-1.0)
- **Exit phrases**: Customize words that trigger conversation ending

## 📊 Feedback Collection

When you exit the chat, the application:

1. Asks for a text review
2. Collects a rating (1-5 stars)
3. Saves this information to `data/feedback.txt`

This data can help improve the application over time.

## 🧠 How It Works

1. The application uses Google's Gemini API for natural language understanding
2. Your messages are sent securely to Gemini's servers
3. The AI generates responses based on its training
4. For feedback collection, the app uses Gemini's function calling feature

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Alphamoris/CLI_chatbot.git).

## 📚 References

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs/text-generation)
- [Function Calling with Gemini](https://ai.google.dev/gemini-api/docs/function-calling)
- [Python dotenv Documentation](https://github.com/theskumar/python-dotenv)

---

<div align="center">

Made with ❤️ by Alphamoris

</div> 