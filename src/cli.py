"""
Command-line interface for playing Blackjack manually.
Use this to test the game before connecting to MCP or AI.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import BlackjackGame, GamePhase


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_game_state(game: BlackjackGame, show_full_dealer: bool = False):
    """Print the current game state in a nice format."""
    state = game.get_state()
    player_state = state['player']
    
    print("\n" + "=" * 50)
    
    # Waiting phase - only show chips
    if game.phase == GamePhase.WAITING:
        print(f"💰 Chips: {player_state['chips']}")
        print("=" * 50)
        print(f"\n📢 {state['message']}")
        print("-" * 50)
        return
    
    # Active game - show full state
    print(f"💰 Chips: {player_state['chips']} | Current Bet: {game.player.current_bet}")
    print("=" * 50)
    
    # Dealer's hand
    print("\n🎩 DEALER'S HAND:")
    dealer = state['dealer']
    if show_full_dealer or game.phase in [GamePhase.DEALER_TURN, GamePhase.COMPLETE]:
        print(f"   Cards: {', '.join(dealer['hand'])}")
        print(f"   Score: {dealer.get('score', '?')}")
    else:
        print(f"   Cards: {', '.join(dealer['hand'])}")
        print(f"   Visible: {dealer.get('visible_score', '?')}")
    
    # Player's hand
    print("\n🃏 YOUR HAND:")
    player = state['player']
    print(f"   Cards: {', '.join(player['hand'])}")
    print(f"   Score: {player['score']}")
    
    # Status
    print("\n" + "-" * 50)
    print(f"📢 {state['message']}")
    print("-" * 50)


def get_valid_bet(max_chips: int) -> int:
    """Get a valid bet amount from user."""
    while True:
        try:
            bet = input(f"\nEnter bet amount (1-{max_chips}): ").strip()
            if bet.lower() == 'q':
                return -1
            bet = int(bet)
            if 1 <= bet <= max_chips:
                return bet
            print(f"Please enter a number between 1 and {max_chips}")
        except ValueError:
            print("Please enter a valid number")


def get_player_action(available_actions: list) -> str:
    """Get player's action choice."""
    action_map = {
        'h': 'hit',
        's': 'stand',
        'd': 'double_down',
        'n': 'new_round',
        'q': 'quit'
    }
    
    print("\nAvailable actions:")
    if 'hit' in available_actions:
        print("  [H] Hit")
    if 'stand' in available_actions:
        print("  [S] Stand")
    if 'double_down' in available_actions:
        print("  [D] Double Down")
    if 'new_round' in available_actions:
        print("  [N] New Round")
    print("  [Q] Quit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice in action_map:
            action = action_map[choice]
            if action == 'quit':
                return 'quit'
            if action in available_actions or action == 'quit':
                return action
        print("Invalid choice. Try again.")


def main():
    print("\n" + "=" * 50)
    print("    🃏 WELCOME TO BLACKJACK 🃏")
    print("=" * 50)
    print("\nStarting with 1000 chips...")
    
    game = BlackjackGame(num_decks=6, starting_chips=1000)
    
    while True:
        if game.phase == GamePhase.WAITING:
            print_game_state(game)
            
            if game.player.chips <= 0:
                print("\n💸 You're out of chips! Game over.")
                play_again = input("Play again? (y/n): ").strip().lower()
                if play_again == 'y':
                    game = BlackjackGame(num_decks=6, starting_chips=1000)
                    continue
                else:
                    break
            
            bet = get_valid_bet(game.player.chips)
            if bet == -1:
                print("\nThanks for playing! 👋")
                break
            
            game.place_bet(bet)
        
        elif game.phase == GamePhase.PLAYER_TURN:
            print_game_state(game)
            
            actions = game.get_available_actions()
            action = get_player_action(actions)
            
            if action == 'quit':
                print("\nThanks for playing! 👋")
                break
            elif action == 'hit':
                game.hit()
            elif action == 'stand':
                game.stand()
            elif action == 'double_down':
                game.double_down()
        
        elif game.phase == GamePhase.COMPLETE:
            print_game_state(game, show_full_dealer=True)
            
            actions = game.get_available_actions()
            action = get_player_action(actions)
            
            if action == 'quit':
                print(f"\nFinal chips: {game.player.chips}")
                print("Thanks for playing! 👋")
                break
            elif action == 'new_round':
                game.new_round()
        
        else:
            # Dealer turn or dealing - these are automatic
            pass


if __name__ == "__main__":
    main()
