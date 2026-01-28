"""
MCP Server for Blackjack Game.
Exposes game functionality as MCP tools.
"""
import json
from mcp.server.fastmcp import FastMCP
from game import BlackjackGame

# Initialize MCP server
mcp = FastMCP("Blackjack MCP Server")

# Game instance (single player for now)
game = BlackjackGame(num_decks=6, player_name="Player", starting_chips=1000)


@mcp.tool()
def get_game_state() -> str:
    """
    Get the current state of the blackjack game.
    Returns player hand, dealer hand (visible cards), scores, chips, and available actions.
    """
    state = game.get_state()
    state["available_actions"] = game.get_available_actions()
    return json.dumps(state, indent=2)


@mcp.tool()
def place_bet(amount: int) -> str:
    """
    Place a bet to start a new round of blackjack.
    
    Args:
        amount: The amount of chips to bet (must be positive and <= your chip count)
    
    Returns:
        Game state after placing bet and dealing initial cards.
    """
    result = game.place_bet(amount)
    if result["success"]:
        result["state"]["available_actions"] = game.get_available_actions()
    return json.dumps(result, indent=2)


@mcp.tool()
def hit() -> str:
    """
    Take a hit - draw another card.
    Can only be used during player's turn.
    
    Returns:
        The card drawn and updated game state.
    """
    result = game.hit()
    if result["success"]:
        result["state"]["available_actions"] = game.get_available_actions()
    return json.dumps(result, indent=2)


@mcp.tool()
def stand() -> str:
    """
    Stand - keep current hand and end turn.
    Dealer will then play their turn.
    
    Returns:
        Final game state including dealer's play and result.
    """
    result = game.stand()
    if result["success"]:
        result["state"]["available_actions"] = game.get_available_actions()
    return json.dumps(result, indent=2)


@mcp.tool()
def double_down() -> str:
    """
    Double down - double your bet, take exactly one more card, then stand.
    Can only be used on initial 2-card hand and requires enough chips.
    
    Returns:
        The card drawn and final game state.
    """
    result = game.double_down()
    if result["success"]:
        result["state"]["available_actions"] = game.get_available_actions()
    return json.dumps(result, indent=2)


@mcp.tool()
def new_round() -> str:
    """
    Start a new round after the previous round is complete.
    Resets hands but keeps chip count.
    
    Returns:
        Fresh game state ready for betting.
    """
    result = game.new_round()
    if result["success"]:
        result["state"]["available_actions"] = game.get_available_actions()
    return json.dumps(result, indent=2)


@mcp.tool()
def reset_game(starting_chips: int = 1000) -> str:
    """
    Reset the entire game with fresh chips.
    
    Args:
        starting_chips: Number of chips to start with (default 1000)
    
    Returns:
        Fresh game state.
    """
    global game
    game = BlackjackGame(num_decks=6, player_name="Player", starting_chips=starting_chips)
    state = game.get_state()
    state["available_actions"] = game.get_available_actions()
    return json.dumps({"success": True, "message": f"Game reset with {starting_chips} chips.", "state": state}, indent=2)


@mcp.tool()
def get_rules() -> str:
    """
    Get the rules of blackjack as implemented in this game.
    
    Returns:
        String explaining the game rules.
    """
    rules = """
    BLACKJACK RULES
    ===============
    
    OBJECTIVE:
    Beat the dealer by getting a hand value closer to 21 without going over.
    
    CARD VALUES:
    - Number cards (2-10): Face value
    - Face cards (J, Q, K): 10
    - Ace: 11 or 1 (automatically adjusted to avoid busting)
    
    GAMEPLAY:
    1. Place your bet
    2. You and dealer each get 2 cards (one dealer card is hidden)
    3. Choose to Hit (take card), Stand (keep hand), or Double Down
    4. If you go over 21, you bust and lose
    5. After you stand, dealer reveals hidden card and plays
    6. Dealer must hit on 16 or less, stand on 17+
    
    PAYOUTS:
    - Blackjack (Ace + 10-value on first 2 cards): 3:2
    - Regular win: 1:1
    - Push (tie): Bet returned
    
    AVAILABLE ACTIONS:
    - place_bet(amount): Start round with a bet
    - hit(): Draw another card
    - stand(): Keep current hand
    - double_down(): Double bet, take one card, stand
    - new_round(): Start fresh round after completion
    - reset_game(): Reset with new chips
    """
    return rules


# Entry point for running the server
if __name__ == "__main__":
    mcp.run()
