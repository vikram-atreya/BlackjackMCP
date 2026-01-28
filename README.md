# 🃏 Blackjack MCP Server

A Model Context Protocol (MCP) server that implements a Blackjack game. Play manually via CLI or connect an AI agent to play through MCP tools.

## Architecture

```
BlackjackMCP/
├── src/
│   ├── server.py      # MCP server - exposes game as tools
│   ├── game.py        # Core game logic & state machine
│   ├── player.py      # Player class - hand, betting, actions
│   ├── dealer.py      # Dealer class - automated dealer logic
│   ├── deck.py        # Card and Deck classes
│   └── cli.py         # Manual play via command line
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Play Manually (CLI)

Test the game logic with manual inputs:

```bash
cd src
python cli.py
```

### 3. Run MCP Server

Start the MCP server for AI agents:

```bash
cd src
python server.py
```

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `get_game_state()` | Get current game state, hands, scores, available actions |
| `place_bet(amount)` | Start a round by placing a bet |
| `hit()` | Draw another card |
| `stand()` | Keep current hand, dealer plays |
| `double_down()` | Double bet, take one card, stand |
| `new_round()` | Start new round after completion |
| `reset_game(chips)` | Reset game with fresh chips |
| `get_rules()` | Get game rules explanation |

## Game Rules

- **Objective**: Get closer to 21 than the dealer without going over
- **Card Values**: 2-10 = face value, J/Q/K = 10, A = 11 or 1
- **Blackjack**: Ace + 10-value card = 3:2 payout
- **Dealer**: Must hit on 16 or less, stand on 17+

## Connecting an AI Agent

Configure your AI agent (Claude, etc.) to use this MCP server:

```json
{
  "mcpServers": {
    "blackjack": {
      "command": "python",
      "args": ["path/to/BlackjackMCP/src/server.py"]
    }
  }
}
```

The AI can then call tools like:
1. `get_game_state()` - See current state
2. `place_bet(100)` - Start with 100 chip bet
3. `hit()` or `stand()` - Make decisions
4. `new_round()` - Play again

## Example Game Flow

```
1. get_game_state()        → See you have 1000 chips, phase: "waiting"
2. place_bet(100)          → Cards dealt, your hand: "K♠, 7♥" (17)
3. stand()                 → Dealer plays, reveals "10♦, 6♣, 5♠" (21)
4. get_game_state()        → Result: dealer_win, chips: 900
5. new_round()             → Ready for next bet
```

## Extending the Game

### Add Split functionality
Edit `player.py` to handle split hands, update `game.py` with split logic.

### Add Insurance
Add insurance option when dealer shows Ace in `game.py`.

### Multi-player
Modify `game.py` to track multiple Player instances.

## License

MIT
Trying to make a MCP server for playing blackjack with an AI dealer and AI players
