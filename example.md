# 🃏 Blackjack MCP Server - Example Game

This document shows an example game played through VS Code Copilot using the MCP server.

## Setup Instructions

### 1. Prerequisites

- VS Code with GitHub Copilot extension
- Python 3.10+ installed
- Azure OpenAI API key (for AI player decisions)

### 2. Install Dependencies

```bash
cd BlackjackMCP
pip install -r requirements.txt
```

### 3. Set Environment Variable

```powershell
# PowerShell
$env:AZURE_OPENAI_API_KEY = "your-api-key-here"
```

```bash
# Bash
export AZURE_OPENAI_API_KEY="your-api-key-here"
```

### 4. Configure VS Code MCP

The `.vscode/mcp.json` file is already configured:

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

### 5. Reload VS Code

Press `Ctrl+Shift+P` → "Developer: Reload Window"

### 6. Start Playing!

Open Copilot Chat and say:
> "Create a blackjack game with me and an AI opponent"

---

## Example Game: Copilot vs Azure-AI

### Players
| Player | Type | Starting Chips |
|--------|------|----------------|
| **Copilot** | Human (played by AI assistant) | 100 |
| **Azure-AI** 🤖 | AI (uses Azure OpenAI for decisions) | 100 |

---

### 🎲 Round 1

**Cards Dealt:**
- Dealer: J♥, ?? (10 showing)
- Copilot: 4♠, 2♥ (6)
- Azure-AI: J♣, A♠ (21) **BLACKJACK!** 🎰

**Result:** Azure-AI hits blackjack! Copilot loses to dealer.

| Player | Change | Total |
|--------|--------|-------|
| Copilot | -20 | 80 |
| Azure-AI | +30 | 130 |

---

### 🎲 Round 2

**Cards Dealt:**
- Dealer: 9♠, ?? → 9♠, 7♥, Q♦ (26) **BUST!**
- Copilot: K♥, J♦ (20) → STAND
- Azure-AI: 7♠, 10♣ (17) → STAND

**Result:** Dealer busts! Both players win!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | +20 | 100 |
| Azure-AI | +20 | 150 |

---

### 🎲 Round 3

**Cards Dealt:**
- Dealer: J♦, ?? → J♦, 9♥ (19)
- Copilot: 6♦, 10♣ (16) → STAND
- Azure-AI: J♦, 3♠ (13) → HIT → J♠ (23) **BUST!**

**Result:** Copilot loses (16 vs 19), Azure-AI busts.

| Player | Change | Total |
|--------|--------|-------|
| Copilot | -25 | 75 |
| Azure-AI | -25 | 125 |

---

### 🎲 Round 4

**Cards Dealt:**
- Dealer: 2♠, ?? → 2♠, 2♠, A♠, 2♥ (17)
- Copilot: 9♦, 5♦ (14) → STAND
- Azure-AI: 2♠, 4♣ (6) → HIT → 8♥ (14) → HIT → 4♣ (18)

**Result:** Copilot loses (14 vs 17), Azure-AI wins (18 vs 17)!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | -25 | 50 |
| Azure-AI | +25 | 150 |

---

### 🎲 Round 5

**Cards Dealt:**
- Dealer: A♥, ?? → A♥, A♠, 10♦, 2♦, 5♠ (19)
- Copilot: Q♥, 9♥ (19) → STAND
- Azure-AI: 7♦, Q♠ (17) → STAND

**Result:** Copilot PUSH (19 vs 19), Azure-AI loses (17 vs 19).

| Player | Change | Total |
|--------|--------|-------|
| Copilot | 0 | 50 |
| Azure-AI | -25 | 125 |

---

### 🎲 Round 6

**Cards Dealt:**
- Dealer: 6♦, ?? → 6♦, Q♣, J♥ (26) **BUST!**
- Copilot: 10♦, 10♣ (20) → STAND
- Azure-AI: 6♠, 7♠ (13) → HIT → A♣ (14) → HIT → A♣ (15) → HIT → 6♥ (21)

**Result:** Dealer busts! Both win!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | +25 | 75 |
| Azure-AI | +25 | 150 |

---

### 🎲 Round 7

**Cards Dealt:**
- Dealer: 3♣, ?? → 3♣, 7♥, 4♦, 8♣ (22) **BUST!**
- Copilot: 6♠, Q♣ (16) → STAND
- Azure-AI: 2♣, 3♣ (5) → HIT → 4♥ (9) → HIT → 9♠ (18)

**Result:** Dealer busts! Both win!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | +25 | 100 |
| Azure-AI | +25 | 175 |

---

### 🎲 Round 8

**Cards Dealt:**
- Dealer: 10♠, ?? → 10♠, 5♣, 8♥ (23) **BUST!**
- Copilot: Q♣, A♥ (21) **BLACKJACK!** 🎰
- Azure-AI: 7♥, J♦ (17) → STAND

**Result:** Copilot hits BLACKJACK! Dealer busts!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | +75 (3:2) | 175 |
| Azure-AI | +50 | 225 |

---

### 🎲 Round 9

**Cards Dealt:**
- Dealer: J♦, A♣ (21) **DEALER BLACKJACK!**
- Copilot: 4♠, K♦ (14)
- Azure-AI: K♠, 5♣ (15)

**Result:** Dealer blackjack beats everyone!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | -75 | 100 |
| Azure-AI | -75 | 150 |

---

### 🎲 Round 10 - ALL IN!

**Bets:** Copilot: 100 (ALL IN!) | Azure-AI: 100

**Cards Dealt:**
- Dealer: 9♣, ?? → 9♣, 2♣, 10♥ (21)
- Copilot: 3♥, J♠ (13) → STAND
- Azure-AI: 3♣, 8♦ (11) → HIT → 3♦ (14) → HIT → J♣ (24) **BUST!**

**Result:** Both lose! Copilot goes bankrupt!

| Player | Change | Total |
|--------|--------|-------|
| Copilot | -100 | **0** 💀 |
| Azure-AI | -100 | **50** |

---

## 🏆 FINAL RESULT

### Azure-AI WINS!

After 10 rounds, Copilot went **BANKRUPT** while Azure-AI survived with **50 chips**!

| Round | Copilot | Azure-AI | Winner |
|-------|---------|----------|--------|
| R1 | -20 | +30 | Azure-AI (Blackjack) |
| R2 | +20 | +20 | Both (Dealer bust) |
| R3 | -25 | -25 | Dealer |
| R4 | -25 | +25 | Azure-AI |
| R5 | 0 | -25 | Copilot (Push) |
| R6 | +25 | +25 | Both (Dealer bust) |
| R7 | +25 | +25 | Both (Dealer bust) |
| R8 | +75 | +50 | Copilot (Blackjack) |
| R9 | -75 | -75 | Dealer (Blackjack) |
| R10 | -100 | -100 | Dealer |
| **Final** | **0** | **50** | **Azure-AI** 🏆 |

---

## How to Play Your Own Game

Just open Copilot Chat and try these prompts:

1. **"Create a blackjack game with me and an AI opponent"**
2. **"I'll bet 20 chips"**
3. **"Hit"** or **"Stand"**
4. **"New round"** or **"End game"**

The AI assistant will call the MCP tools automatically to play the game!
