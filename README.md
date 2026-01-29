# 🃏 Blackjack MCP Server

A **Model Context Protocol (MCP)** server that implements a multiplayer Blackjack game. Play against AI opponents powered by Azure OpenAI, or connect VS Code Copilot to play through natural language.

> **What is MCP?** MCP is a protocol that lets AI assistants (like GitHub Copilot, Claude) interact with external tools. This project exposes Blackjack as MCP tools that AI can call.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎮 **Multiplayer** | Up to 6 players at a table |
| 🤖 **AI Opponents** | Bots that use Azure OpenAI/LLM for decisions |
| 🔌 **MCP Protocol** | Connect AI assistants like VS Code Copilot or Claude |
| 🎯 **Turn-by-turn** | Clear game flow with state tracking |
| 🐳 **Docker Support** | Containerized for easy deployment |
| 💬 **Multiple CLIs** | Single-player, multiplayer, and AI modes |

## 📁 Project Structure

```
BlackjackMCP/
├── src/
│   ├── server.py           # 🔌 MCP server - exposes game as tools
│   ├── game.py             # 🎮 Single-player game logic
│   ├── game_multiplayer.py # 👥 Multiplayer game logic
│   ├── player.py           # 🧑 Player class - hand, betting
│   ├── dealer.py           # 🎩 Dealer class - automated logic
│   ├── deck.py             # 🃏 Card and Deck classes
│   ├── ai_player.py        # 🤖 AI player using LLM for decisions
│   ├── ai_advisor.py       # 💡 AI advisor for human players
│   ├── cli.py              # ⌨️ Single-player CLI
│   ├── cli_multiplayer.py  # ⌨️ Multiplayer CLI (humans only)
│   └── cli_with_ai.py      # ⌨️ Human vs AI CLI
├── .vscode/
│   └── mcp.json            # VS Code Copilot MCP configuration
├── Dockerfile              # 🐳 Container build instructions
├── docker-compose.yml      # 🐳 Multi-service orchestration
├── requirements.txt        # 📦 Python dependencies
├── example.md              # 📖 Example game walkthrough
└── README.md
```

## 🚀 Quick Start

### Option 1: Local Python

```bash
# Clone the repo
git clone https://github.com/vikram-atreya/BlackjackMCP.git
cd BlackjackMCP

# Install dependencies
pip install -r requirements.txt

# Set API key (for AI features)
# PowerShell:
$env:AZURE_OPENAI_API_KEY = "your-api-key"
# Bash:
export AZURE_OPENAI_API_KEY="your-api-key"

# Play!
cd src
python cli_with_ai.py      # Human vs AI opponents
python cli_multiplayer.py  # Multiplayer (humans only)
python cli.py              # Single player
```

### Option 2: Docker

```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your API key

# Build and run CLI game
docker compose --profile cli run --rm blackjack-cli
```

## 🔌 Using with VS Code Copilot (MCP)

This is the **main feature** of this project - playing Blackjack through AI!

### Setup

1. Open this workspace in VS Code
2. Set your `AZURE_OPENAI_API_KEY` environment variable
3. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")

### Play via Chat

Just talk to Copilot naturally:

```
You: "Create a blackjack game with me and an AI opponent"
You: "I'll bet 20 chips"
You: "Hit"
You: "Stand"
You: "Let the AI play"
You: "New round"
```

Copilot calls the MCP tools automatically! See [example.md](example.md) for a full game walkthrough.

## 🛠️ MCP Tools Reference

| Tool | Description |
|------|-------------|
| `create_game()` | Create a new game table |
| `add_player(name)` | Add a human player (100 chips default) |
| `add_ai_player(name)` | Add an AI opponent |
| `start_game()` | Begin the game (betting phase) |
| `place_bet(player, amount)` | Player places their bet |
| `hit(player)` | Draw another card |
| `stand(player)` | Keep current hand |
| `double_down(player)` | Double bet, take one card |
| `ai_play_turn()` | Let AI player decide (uses LLM) |
| `get_game_state()` | Get full game state as JSON |
| `new_round()` | Start next round |
| `end_game()` | End game, show final standings |
| `get_rules()` | Get game rules |

## 🎯 Game Flow

```
1. create_game()              → Table created with 6 decks
2. add_player("Alice")        → Alice joins with 100 chips
3. add_ai_player()            → Bot-Alpha joins
4. start_game()               → Betting phase begins
5. place_bet("Alice", 20)     → Alice bets 20 chips
6. place_bet("Bot-Alpha", 10) → Bot bets 10, cards are dealt!
7. hit("Alice")               → Alice draws a card
8. stand("Alice")             → Alice ends turn
9. ai_play_turn()             → Bot-Alpha asks LLM and decides
10. (dealer plays automatically when all players done)
11. get_game_state()          → See results and chip counts
12. new_round()               → Play again!
```

## 🃏 Blackjack Rules

| Rule | Description |
|------|-------------|
| **Objective** | Get closer to 21 than dealer without going over |
| **Card Values** | 2-10 = face value, J/Q/K = 10, Ace = 11 or 1 |
| **Blackjack** | Ace + 10-value card on first 2 cards = 3:2 payout |
| **Dealer** | Must hit on ≤16, must stand on ≥17 |
| **Bust** | Going over 21 = automatic loss |
| **Push** | Tie with dealer = bet returned |

## ⚙️ Configuration

### VS Code MCP (`.vscode/mcp.json`)

```json
{
  "servers": {
    "blackjack": {
      "command": "python",
      "args": ["${workspaceFolder}/src/server.py"],
      "env": {
        "AZURE_OPENAI_API_KEY": "${env:AZURE_OPENAI_API_KEY}",
        "AZURE_OPENAI_ENDPOINT": "https://your-endpoint.openai.azure.com/"
      },
      "alwaysAllow": [
        "create_game", "add_player", "add_ai_player", "start_game",
        "place_bet", "hit", "stand", "double_down", "ai_play_turn",
        "new_round", "end_game", "get_game_state", "get_rules"
      ]
    }
  }
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |

## 🐳 Docker

```bash
# Build the image
docker build -t blackjack-mcp .

# Run CLI game interactively
docker compose --profile cli run --rm blackjack-cli

# Run MCP server
docker compose up blackjack-mcp
```

## 📚 What I Learned Building This

This project was built to learn about:

1. **MCP (Model Context Protocol)** - How AI assistants interact with external tools
2. **Python OOP** - Classes, decorators, enums, type hints
3. **State Machines** - Game phases (lobby → betting → playing → complete)
4. **Azure OpenAI** - Integrating LLM for AI player decisions
5. **Docker** - Containerizing Python applications

## 🔗 Related Files

- [example.md](example.md) - Full game walkthrough with VS Code Copilot
- [strategies.md](strategies.md) - Blackjack strategy notes

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

Built with ❤️ as a learning project for MCP and AI integration.
