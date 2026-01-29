"""
MCP Server for Blackjack Game.
Exposes multiplayer game functionality as MCP tools.
Supports human players and AI opponents with turn-by-turn gameplay.
"""
import json
from mcp.server.fastmcp import FastMCP
from game_multiplayer import MultiPlayerBlackjack, GamePhase
from ai_player import AIPlayerStrategy

# Initialize MCP server
mcp = FastMCP("Blackjack MCP Server")

# Game instance - multiplayer
game: MultiPlayerBlackjack = None
ai_players: set = set()  # Track which players are AI


def _get_state_with_context() -> dict:
    """Get game state with additional context for AI."""
    if game is None:
        return {"error": "No game in progress. Use create_game to start."}
    
    state = game.get_state()
    state["phase"] = game.phase.value
    state["ai_players"] = list(ai_players)
    
    # Add available actions based on phase
    if game.phase == GamePhase.LOBBY:
        state["available_actions"] = ["add_player", "add_ai_player", "start_game"]
    elif game.phase == GamePhase.BETTING:
        state["available_actions"] = ["place_bet"]
    elif game.phase == GamePhase.PLAYER_TURN:
        state["available_actions"] = ["hit", "stand", "double_down"]
    elif game.phase == GamePhase.COMPLETE:
        state["available_actions"] = ["new_round", "end_game"]
    else:
        state["available_actions"] = []
    
    return state


@mcp.tool()
def create_game(num_decks: int = 6) -> str:
    """
    Create a new blackjack game table. Call this first before adding players.
    
    Args:
        num_decks: Number of decks to use (default 6, standard casino)
    
    Returns:
        Confirmation and instructions to add players.
    """
    global game, ai_players
    game = MultiPlayerBlackjack(num_decks=num_decks)
    ai_players = set()
    
    return json.dumps({
        "success": True,
        "message": f"Game table created with {num_decks} decks. Add players using add_player or add_ai_player.",
        "state": _get_state_with_context()
    }, indent=2)


@mcp.tool()
def add_player(name: str, chips: int = 100) -> str:
    """
    Add a human player to the game. Can only be done in lobby phase.
    
    Args:
        name: Player's name (must be unique)
        chips: Starting chips (default 100)
    
    Returns:
        Updated game state with new player.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists. Use create_game first."})
    
    result = game.add_player(name)
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def add_ai_player(name: str = None, chips: int = 100) -> str:
    """
    Add an AI opponent to the game. AI players make decisions automatically using LLM.
    
    Args:
        name: AI player name (auto-generated if not provided)
        chips: Starting chips (default 100)
    
    Returns:
        Updated game state with new AI player.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists. Use create_game first."})
    
    # Generate AI name if not provided
    ai_names = ["Bot-Alpha", "Bot-Beta", "Bot-Gamma", "Bot-Delta"]
    if name is None:
        for ai_name in ai_names:
            if ai_name not in ai_players:
                name = ai_name
                break
        if name is None:
            name = f"Bot-{len(ai_players) + 1}"
    
    result = game.add_player(name)
    if result["success"]:
        ai_players.add(name)
        result["message"] = f"AI player '{name}' joined the game."
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def start_game() -> str:
    """
    Start the game after all players have joined. Moves to betting phase.
    Requires at least 1 player.
    
    Returns:
        Game state in betting phase.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists. Use create_game first."})
    
    result = game.start_betting()
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def place_bet(player_name: str, amount: int) -> str:
    """
    Place a bet for a specific player. All players must bet before cards are dealt.
    For AI players, you can call this or let them bet automatically.
    
    Args:
        player_name: Name of the player placing the bet
        amount: Bet amount (must be <= player's chips)
    
    Returns:
        Updated game state. When all bets are placed, cards are dealt automatically.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists. Use create_game first."})
    
    result = game.place_bet(player_name, amount)
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def get_game_state() -> str:
    """
    Get the current state of the blackjack game.
    Shows all players, hands, the dealer's visible card, current turn, and available actions.
    
    Returns:
        Complete game state as JSON.
    """
    return json.dumps(_get_state_with_context(), indent=2)


@mcp.tool()
def hit(player_name: str = None) -> str:
    """
    Current player takes a hit - draws another card.
    
    Args:
        player_name: Optional - verify it's the correct player's turn
    
    Returns:
        The card drawn and updated game state.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    # Verify correct player if name provided
    current = game.get_state().get("current_player")
    if player_name and player_name != current:
        return json.dumps({"success": False, "error": f"It's {current}'s turn, not {player_name}'s."})
    
    result = game.hit(current)
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def stand(player_name: str = None) -> str:
    """
    Current player stands - keeps their hand and ends their turn.
    
    Args:
        player_name: Optional - verify it's the correct player's turn
    
    Returns:
        Updated game state with next player's turn or dealer play.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    current = game.get_state().get("current_player")
    if player_name and player_name != current:
        return json.dumps({"success": False, "error": f"It's {current}'s turn, not {player_name}'s."})
    
    result = game.stand(current)
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def double_down(player_name: str = None) -> str:
    """
    Current player doubles down - doubles bet, takes exactly one card, then stands.
    Only available on first two cards if player has enough chips.
    
    Args:
        player_name: Optional - verify it's the correct player's turn
    
    Returns:
        Card drawn and final game state.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    current = game.get_state().get("current_player")
    if player_name and player_name != current:
        return json.dumps({"success": False, "error": f"It's {current}'s turn, not {player_name}'s."})
    
    result = game.double_down(current)
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def ai_play_turn() -> str:
    """
    Let the current AI player make their decision using LLM.
    Call this when it's an AI player's turn.
    
    Returns:
        The AI's decision and reasoning, plus updated game state.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    state = game.get_state()
    current = state.get("current_player")
    
    if current not in ai_players:
        return json.dumps({"success": False, "error": f"{current} is not an AI player. Use hit/stand/double_down."})
    
    # Find current player's data
    player_data = None
    for p in state["players"]:
        if p["name"] == current:
            player_data = p
            break
    
    if not player_data:
        return json.dumps({"success": False, "error": "Could not find player data."})
    
    dealer_data = state.get("dealer", {})
    dealer_visible_card = dealer_data.get("hand", ["?"])[0] if dealer_data.get("hand") else "?"
    dealer_score = dealer_data.get("visible_score", 10)
    player_hand = player_data.get("hand", [])
    player_score = player_data.get("score", 0)
    can_double = len(player_hand) == 2 and player_data.get("chips", 0) >= player_data.get("current_bet", 0)
    
    # Get AI decision
    action, reason = AIPlayerStrategy.decide(
        player_hand=player_hand,
        player_score=player_score,
        dealer_visible_card=dealer_visible_card,
        dealer_visible_score=dealer_score,
        can_double=can_double,
        num_cards=len(player_hand)
    )
    
    # Execute the action
    if action == "hit":
        result = game.hit(current)
    elif action == "stand":
        result = game.stand(current)
    elif action == "double_down" and can_double:
        result = game.double_down(current)
    else:
        result = game.hit(current)  # Fallback
    
    result["ai_decision"] = {
        "player": current,
        "action": action,
        "reason": reason
    }
    
    if result["success"]:
        result["state"] = _get_state_with_context()
    
    return json.dumps(result, indent=2)


@mcp.tool()
def new_round() -> str:
    """
    Start a new round after the current round is complete.
    All players keep their chips and a fresh round begins.
    
    Returns:
        Fresh game state ready for betting.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    result = game.new_round()
    if result["success"]:
        result["state"] = _get_state_with_context()
    return json.dumps(result, indent=2)


@mcp.tool()
def end_game() -> str:
    """
    End the current game and show final standings.
    
    Returns:
        Final chip counts for all players.
    """
    if game is None:
        return json.dumps({"success": False, "error": "No game exists."})
    
    state = game.get_state()
    standings = []
    for p in state["players"]:
        standings.append({"name": p["name"], "chips": p["chips"], "is_ai": p["name"] in ai_players})
    
    standings.sort(key=lambda x: x["chips"], reverse=True)
    
    return json.dumps({
        "success": True,
        "message": "Game ended!",
        "final_standings": standings
    }, indent=2)


@mcp.tool()
def get_rules() -> str:
    """
    Get the rules of blackjack and how to use this MCP server.
    
    Returns:
        Game rules and available commands.
    """
    rules = """
BLACKJACK MCP SERVER - RULES & COMMANDS
=======================================

GAME FLOW:
1. create_game() - Create a new table
2. add_player(name) or add_ai_player() - Add players
3. start_game() - Begin the game
4. place_bet(player, amount) - Each player bets
5. hit/stand/double_down or ai_play_turn() - Play turns
6. new_round() - Play again after round ends

BLACKJACK RULES:
- Beat dealer by getting closer to 21 without going over
- Number cards = face value, Face cards = 10, Ace = 11 or 1
- Blackjack (Ace + 10) pays 3:2
- Dealer hits on 16 or less, stands on 17+

ACTIONS:
- hit(): Draw another card
- stand(): Keep hand, end turn
- double_down(): Double bet, take one card, stand
- ai_play_turn(): Let AI player decide (uses LLM)

PAYOUTS:
- Blackjack: 3:2
- Win: 1:1  
- Push: Bet returned
"""
    return rules


# Entry point for running the server
if __name__ == "__main__":
    mcp.run()
