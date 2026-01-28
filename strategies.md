# AI Agent Framework Strategies

## Framework Options for AI Agents Playing Blackjack

### Option 1: **Orchestrator Pattern** (Recommended to start)

```
┌─────────────────────────────────────────────────────┐
│                  Game Orchestrator                   │
│              (Python script + LLM API)               │
├─────────────────────────────────────────────────────┤
│  1. Runs game logic locally (game_multiplayer.py)   │
│  2. For each player's turn:                         │
│     → Send game state to LLM API                    │
│     → Get decision (hit/stand/double)               │
│     → Execute action                                │
│  3. Log results, track statistics                   │
└─────────────────────────────────────────────────────┘
```

**Pros:** Simple, no MCP complexity, works with any LLM API  
**Cons:** Not using MCP (but good for testing AI strategies)

---

### Option 2: **MCP Server + AI Client**

```
┌──────────────┐         ┌──────────────────┐
│  Blackjack   │  MCP    │    AI Agent      │
│  MCP Server  │◄───────►│  (Claude, etc.)  │
│              │  tools  │                  │
└──────────────┘         └──────────────────┘
                               │
                    Uses tools: get_game_state(),
                    place_bet(), hit(), stand()
```

**Pros:** Uses MCP as intended, AI learns to use tools  
**Cons:** Single player only (MCP is 1:1)

---

### Option 3: **Multi-Agent with Personalities**

```
┌─────────────────────────────────────────────────────┐
│                  Game Orchestrator                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Agent: Rick │  │Agent: Sarah │  │ Agent: Bot  │ │
│  │ "Aggressive"│  │"Conservative│  │ "Basic      │ │
│  │ Risk-taker  │  │ Calculator" │  │  Strategy"  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│        │                │                │         │
│        └────────────────┼────────────────┘         │
│                         ▼                          │
│              LLM API (with persona prompts)        │
│                    or Rule-based                   │
└─────────────────────────────────────────────────────┘
```

**Pros:** Interesting dynamics, can compare strategies  
**Cons:** More complex, higher API costs

---

## Recommended Implementation: Option 1

Build an `ai_game.py` that:

```python
# Pseudo-structure
class AIPlayer:
    def __init__(self, name: str, strategy: str, use_llm: bool = True):
        self.name = name
        self.strategy = strategy  # "aggressive", "conservative", "basic_strategy"
        self.use_llm = use_llm
    
    def decide(self, game_state: dict) -> str:
        if self.use_llm:
            return self._ask_llm(game_state)
        else:
            return self._basic_strategy(game_state)

class AIGameRunner:
    def __init__(self, players: list[AIPlayer]):
        self.game = MultiPlayerBlackjack()
        self.players = players
    
    def play_rounds(self, num_rounds: int):
        # Run multiple rounds, track statistics
        pass
```

---

## Questions to Decide

1. **AI vs AI only, or human + AI mixed?**
2. **LLM API (OpenAI/Anthropic) or rule-based bots first?**
3. **Track statistics (win rate, chip history)?**

---

## Basic Strategy Reference

Standard blackjack basic strategy for rule-based bot:

| Player Score | Dealer Shows 2-6 | Dealer Shows 7-A |
|--------------|------------------|------------------|
| 17+          | Stand            | Stand            |
| 13-16        | Stand            | Hit              |
| 12           | Stand (3-6)      | Hit              |
| 11           | Double           | Double           |
| 10           | Double           | Hit (10-A)       |
| 9            | Double (3-6)     | Hit              |
| 8 or less    | Hit              | Hit              |

### Soft Hands (with Ace)

| Hand    | Dealer Shows 2-6 | Dealer Shows 7-A |
|---------|------------------|------------------|
| A,8-A,9 | Stand            | Stand            |
| A,7     | Double/Stand     | Hit              |
| A,6     | Double           | Hit              |
| A,2-A,5 | Double (4-6)     | Hit              |
