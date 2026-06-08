# Telegram AI Chatbot

A production-ready Telegram AI chatbot powered by Google Gemini with advanced features including conversation memory, persona management, multi-API key support with rotation, whitelist access control, rate limiting, and comprehensive admin statistics.

## Features

### Core Features
- **Multi-Chat Support**: Private chats, groups, and supergroups
- **Conversation Memory**: Store and include previous messages as context
- **Commands**:
  - `/newchat` - Clear conversation history
  - `/persona <text>` - Set custom AI persona
  - `/showpersona` - Display current persona
  - `/resetpersona` - Reset to default persona
  - `/help` - Display help information

### Advanced Features
- **Multi API Key Rotation**: Automatic key switching on quota/rate limit/failures
- **Access Control**: Whitelist system for users and groups
- **Rate Limiting**: 20 requests per hour (configurable)
- **Admin Statistics**: View user stats, chat stats, and API key usage
- **VPN Support**: Built-in VPN proxy configuration
- **Structured Logging**: Comprehensive logging of all operations
- **SQLite Database**: Automatic schema creation on startup

## Prerequisites

- Python 3.12+
- Telegram Bot Token (from BotFather)
- Google Gemini API Key(s)
- pip package manager

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd telegram-ai-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `GEMINI_API_KEYS`: Your Google Gemini API keys (comma-separated)
- `ADMIN_IDS`: Administrator user IDs
- `WHITELIST_*`: Whitelist configuration if needed

### 5. Run the Bot
```bash
python main.py
```

## Configuration Guide

### Basic Setup
```env
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEYS=your_api_key_here
ADMIN_IDS=your_user_id
```

### VPN Configuration
```env
USE_VPN=true
VPN_PROXY_URL=http://proxy-ip:proxy-port
# or
VPN_PROXY_URL=socks5://proxy-ip:proxy-port
```

### Access Control
```env
WHITELIST_ENABLED=true
WHITELIST_USERS=123456789,987654321
WHITELIST_GROUPS=-100111111111,-100222222222
```

### Rate Limiting
```env
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_PERIOD_HOURS=1
```

## Commands

### User Commands
- `/help` - Show help message
- `/newchat` - Clear conversation history
- `/persona <text>` - Set custom persona
- `/showpersona` - Show current persona
- `/resetpersona` - Reset persona to default

### Admin Commands
- `/adminstats` - View statistics
- `/allowedusers` - Show allowed users
- `/allowedgroups` - Show allowed groups

## Group Behavior

To reduce API costs, the bot in groups responds only when:
- Mentioned directly
- Replied to with a message
- A command is used

Regular messages in groups are ignored.

## Database Schema

Automatically created tables:
- `users` - User information and personas
- `chats` - Chat history per user
- `messages` - Individual messages with context
- `statistics` - Operation statistics
- `api_key_stats` - API key usage tracking

## Logging

Logs are stored in the `logs/` directory with the following information:
- All requests and responses
- Errors and exceptions
- API failures and key switching events
- Unauthorized access attempts
- Admin actions

## Architecture

### Project Structure
```
telegram-ai-chatbot/
├── main.py                 # Entry point
├── bot/
│   ├── client.py          # Aiogram bot client setup
├── handlers/
│   ├── commands.py        # Command handlers
│   ├── messages.py        # Message handlers
│   ├── errors.py          # Error handlers
├── services/
│   ├── gemini.py          # Gemini AI service with key rotation
│   ├── rate_limiter.py    # Rate limiting service
│   └── statistics.py      # Statistics service
├── providers/
│   └── gemini_provider.py # Gemini API provider
├── database/
│   ├── db.py              # Database initialization
│   ├── models.py          # Data models
│   └── queries.py         # Database queries
├── middlewares/
│   ├── auth.py            # Authentication middleware
│   ├── rate_limit.py      # Rate limiting middleware
│   └── logging.py         # Logging middleware
├── config/
│   ├── settings.py        # Settings configuration
│   └── constants.py       # Constants
└── logs/                  # Log files directory
```

### Design Patterns
- **Async/Await**: Fully asynchronous architecture
- **Dependency Injection**: Service-based architecture
- **Middleware Pipeline**: Request/response middleware
- **Database Abstraction**: Query layer abstraction
- **Error Handling**: Comprehensive exception handling

## Multi API Key Rotation

The bot automatically rotates Gemini API keys when:
- Quota is exceeded
- Rate limit is reached
- Temporary provider failures occur
- Timeout occurs

Keys are configured as comma-separated values:
```env
GEMINI_API_KEYS=key1,key2,key3,key4
```

## Troubleshooting

### Bot Not Starting
- Check `TELEGRAM_BOT_TOKEN` is valid
- Ensure all required dependencies are installed
- Check logs in `logs/` directory

### API Errors
- Verify `GEMINI_API_KEYS` are valid
- Check API quota hasn't been exceeded
- Review logs for detailed error information

### Rate Limiting Issues
- Adjust `RATE_LIMIT_REQUESTS` if needed
- Check user's current rate limit status
- Review statistics with `/adminstats`

### VPN Connection Issues
- Verify `VPN_PROXY_URL` is accessible
- Check proxy format: `http://ip:port` or `socks5://ip:port`
- Test proxy connectivity independently

## Performance

- Async I/O for all operations
- Connection pooling for database
- Efficient API key rotation
- Minimal memory footprint
- Scalable for multiple concurrent users

## Security

- Whitelist-based access control
- Secure environment variable handling
- User activity logging
- Admin-only statistics access
- VPN proxy support for enhanced privacy

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please refer to the GitHub repository.
