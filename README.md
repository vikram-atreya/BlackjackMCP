# 🃏 Blackjack MCP Server

A Model Context Protocol (MCP) server that implements a multiplayer Blackjack game. Play against AI opponents that use LLM for decisions, or connect VS Code Copilot to play through MCP tools.

## Features

- 🎮 **Multiplayer** - Up to 6 players at a table
- 🤖 **AI Opponents** - Bots that use Azure OpenAI/LLM for decisions
- 🔌 **MCP Protocol** - Connect AI assistants like VS Code Copilot or Claude
- 🎯 **Turn-by-turn** - Clear game flow with state tracking

## Architecture

```
BlackjackMCP/
├── src/
│   ├── server.py           # MCP server - exposes game as tools
│   ├── game.py             # Single-player game logic
│   ├── game_multiplayer.py # Multiplayer game logic
│   ├── player.py           # Player class - hand, betting
│   ├── dealer.py           # Dealer class - automated logic
│   ├── deck.py             # Card and Deck classes
│   ├── ai_player.py        # AI player using LLM for decisions
│   ├── ai_advisor.py       # AI advisor for human players
│   ├── cli.py              # Single-player CLI
│   ├── cli_multiplayer.py  # Multiplayer CLI
│   └── cli_with_ai.py      # Human vs AI CLI
├── .vscode/
│   └── mcp.json            # VS Code Copilot MCP config
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key (for AI features)

```powershell
# PowerShell
$env:AZURE_OPENAI_API_KEY = "your-api-key"

# Or Bash
export AZURE_OPENAI_API_KEY="your-api-key"
```

### 3. Play via CLI

```bash
cd src
python cli_with_ai.py      # Human vs AI opponents
python cli_multiplayer.py  # Multiplayer (humans only)
python cli.py              # Single player
```

## Using with VS Code Copilot (MCP)

### Setup

1. Open this workspace in VS Code
2. The `.vscode/mcp.json` is already configured
3. Set your `AZURE_OPENAI_API_KEY` environment variable
4. Reload VS Code window

### Playing via Copilot

Just chat with Copilot:

```
"Create a blackjack game with me and one AI opponent"
"I'll bet 20 chips"
"Hit me"
"Let the AI play its turn"
```

Copilot will use the MCP tools automatically!

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `create_game()` | Create a new game table |
| `add_player(name, chips)` | Add a human player |
| `add_ai_player(name, chips)` | Add an AI opponent |
| `start_game()` | Begin the game (betting phase) |
| `place_bet(player, amount)` | Player places their bet |
| `hit(player)` | Draw another card |
| `stand(player)` | Keep current hand |
| `double_down(player)` | Double bet, take one card |
| `ai_play_turn()` | Let AI player decide (uses LLM) |
| `get_game_state()` | Get full game state |
| `new_round()` | Start next round |
| `end_game()` | End game, show standings |
| `get_rules()` | Get game rules |

## Game Flow

```
1. create_game()           → Table created
2. add_player("Alice")     → Alice joins with 100 chips
3. add_ai_player()         → Bot-Alpha joins
4. start_game()            → Betting phase begins
5. place_bet("Alice", 20)  → Alice bets 20
6. place_bet("Bot-Alpha", 10) → Bot bets 10, cards dealt!
7. hit("Alice")            → Alice draws a card
8. stand("Alice")          → Alice ends turn
9. ai_play_turn()          → Bot-Alpha decides via LLM
10. (dealer plays automatically when all done)
11. get_game_state()       → See results
12. new_round()            → Play again!
```

## Game Rules

- **Objective**: Get closer to 21 than dealer without busting
- **Card Values**: 2-10 = face value, J/Q/K = 10, Ace = 11 or 1
- **Blackjack**: Ace + 10-value = 3:2 payout
- **Dealer**: Must hit on ≤16, stand on ≥17

## Configuration

Edit `.vscode/mcp.json` to customize:

```json
{
  "servers": {
    "blackjack": {
      "command": "python",
      "args": ["${workspaceFolder}/src/server.py"],
      "env": {
        "AZURE_OPENAI_API_KEY": "${env:AZURE_OPENAI_API_KEY}",
        "AZURE_OPENAI_ENDPOINT": "https://your-endpoint.openai.azure.com/"
      }
    }
  }
}
```

## Docker

### Build and Run

```bash
# Build the image
docker build -t blackjack-mcp .

# Run CLI game
docker compose --profile cli run --rm blackjack-cli

# Run MCP server (for development)
docker compose up blackjack-mcp
```

### Environment Setup

```bash
# Copy example env file
cp .env.example .env

# Edit with your API key
notepad .env
```

## Learn More

See [example.md](example.md) for a complete game walkthrough with VS Code Copilot.
