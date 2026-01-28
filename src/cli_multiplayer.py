"""
Multi-player command-line interface for Blackjack.
Supports multiple players with persistent chip tracking.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_multiplayer import MultiPlayerBlackjack, GamePhase


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_game_state(game: MultiPlayerBlackjack):
    """Print the current game state."""
    state = game.get_state()
    
    print("\n" + "=" * 60)
    
    # LOBBY phase - minimal display
    if game.phase == GamePhase.LOBBY:
        print("🎰 BLACKJACK LOBBY")
        print("=" * 60)
        if state['players']:
            print("\n👥 Players at table:")
            for p in state['players']:
                print(f"   • {p['name']}: {p['chips']} chips")
        else:
            print("\n   No players at table yet.")
        print("\n" + game.get_player_summary())
        print("\n" + "-" * 60)
        print(f"📢 {state['message']}")
        print("-" * 60)
        return
    
    # BETTING phase
    if game.phase == GamePhase.BETTING:
        print("💵 BETTING PHASE")
        print("=" * 60)
        print("\n👥 Players:")
        for p in state['players']:
            bet_status = f"Bet: {p['current_bet']}" if p['current_bet'] > 0 else "Waiting to bet..."
            print(f"   • {p['name']}: {p['chips']} chips | {bet_status}")
        print("\n" + "-" * 60)
        print(f"📢 {state['message']}")
        print("-" * 60)
        return
    
    # ACTIVE GAME - show full state
    print("🃏 BLACKJACK")
    print("=" * 60)
    
    # Dealer's hand
    if state['dealer']:
        print("\n🎩 DEALER'S HAND:")
        dealer = state['dealer']
        print(f"   Cards: {', '.join(dealer['hand'])}")
        if game.phase in [GamePhase.DEALER_TURN, GamePhase.COMPLETE]:
            print(f"   Score: {dealer.get('score', '?')}")
        else:
            print(f"   Visible: {dealer.get('visible_score', '?')}")
    
    # Status message FIRST (for COMPLETE phase, show before results)
    if game.phase == GamePhase.COMPLETE:
        print("\n" + "-" * 60)
        print(f"📢 {state['message']}")
        print("-" * 60)
    
    # All players' hands
    print("\n👥 PLAYERS:")
    for p in state['players']:
        current = " 👈" if p['name'] == state['current_player'] else ""
        result = ""
        if p['name'] in state['results']:
            result_val = state['results'][p['name']]
            result_emoji = {
                'player_blackjack': '🎰 BLACKJACK!',
                'player_win': '✅ WIN',
                'dealer_win': '❌ LOSE',
                'push': '🤝 PUSH',
                'player_bust': '💥 BUST'
            }
            result = f" | {result_emoji.get(result_val, result_val)}"
        
        print(f"\n   {p['name']}{current}{result}")
        print(f"   💰 {p['chips']} chips | Bet: {p['current_bet']}")
        if p['hand']:
            print(f"   🃏 {', '.join(p['hand'])} (Score: {p['score']})")
    
    # Status message AFTER (for non-COMPLETE phases)
    if game.phase != GamePhase.COMPLETE:
        print("\n" + "-" * 60)
        print(f"📢 {state['message']}")
        print("-" * 60)


def get_player_names() -> list:
    """Get player names from user."""
    # First ask how many players
    while True:
        try:
            inp = input("\nHow many players? (1-7, q to quit): ").strip()
            if inp.lower() == 'q':
                return None
            num_players = int(inp)
            if 1 <= num_players <= 7:
                break
            print("Please enter a number between 1 and 7")
        except ValueError:
            print("Please enter a valid number")
    
    # Then ask for each name
    names = []
    for i in range(num_players):
        while True:
            name = input(f"\nPlayer {i + 1} name: ").strip()
            if name.lower() == 'q':
                return None
            if not name:
                print("Please enter a name")
                continue
            if name.lower() in [n.lower() for n in names]:
                print(f"{name} already added, choose a different name")
                continue
            names.append(name)
            break
    
    return names


def get_valid_bet(player_name: str, max_chips: int) -> int:
    """Get a valid bet amount from user."""
    while True:
        try:
            bet = input(f"\n{player_name}, enter bet (1-{max_chips}, q to quit): ").strip()
            if bet.lower() == 'q':
                return -1
            bet = int(bet)
            if 1 <= bet <= max_chips:
                return bet
            print(f"Please enter a number between 1 and {max_chips}")
        except ValueError:
            print("Please enter a valid number")


def get_player_action(player_name: str, available_actions: list) -> str:
    """Get player's action choice."""
    action_map = {
        'h': 'hit',
        's': 'stand',
        'd': 'double_down',
        'q': 'quit'
    }
    
    print(f"\n{player_name}'s turn:")
    if 'hit' in available_actions:
        print("  [H] Hit")
    if 'stand' in available_actions:
        print("  [S] Stand")
    if 'double_down' in available_actions:
        print("  [D] Double Down")
    print("  [Q] Quit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice in action_map:
            action = action_map[choice]
            if action == 'quit':
                return 'quit'
            if action in available_actions:
                return action
        print("Invalid choice. Try again.")


def get_end_round_action() -> str:
    """Get action after round ends."""
    print("\nWhat next?")
    print("  [N] New Round (same players)")
    print("  [L] Back to Lobby (add/remove players)")
    print("  [Q] Quit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice == 'n':
            return 'new_round'
        elif choice == 'l':
            return 'lobby'
        elif choice == 'q':
            return 'quit'
        print("Invalid choice. Try again.")


def main():
    print("\n" + "=" * 60)
    print("    🃏 MULTIPLAYER BLACKJACK 🃏")
    print("=" * 60)
    print("\nEach new player starts with 100 chips.")
    print("Returning players keep their chips!")
    
    game = MultiPlayerBlackjack(num_decks=6)
    
    while True:
        # ===== LOBBY PHASE =====
        if game.phase == GamePhase.LOBBY:
            print_game_state(game)
            
            names = get_player_names()
            if names is None:
                print("\nThanks for playing! 👋")
                break
            
            if not names:
                print("Need at least one player!")
                continue
            
            # Add all players
            for name in names:
                result = game.add_player(name)
                print(f"   {result['message']}")
            
            if game.active_players:
                game.start_betting()
        
        # ===== BETTING PHASE =====
        elif game.phase == GamePhase.BETTING:
            print_game_state(game)
            
            # Find players who haven't bet yet
            for player in game.active_players:
                if player.current_bet == 0:
                    bet = get_valid_bet(player.name, player.chips)
                    if bet == -1:
                        print("\nThanks for playing! 👋")
                        return
                    
                    result = game.place_bet(player.name, bet)
                    if not result['success']:
                        print(f"   {result['message']}")
                    
                    # Check if game moved to next phase
                    if game.phase != GamePhase.BETTING:
                        break
        
        # ===== PLAYER TURN PHASE =====
        elif game.phase == GamePhase.PLAYER_TURN:
            print_game_state(game)
            
            current = game.current_player
            if current:
                actions = game.get_available_actions(current.name)
                action = get_player_action(current.name, actions)
                
                if action == 'quit':
                    print("\nThanks for playing! 👋")
                    break
                elif action == 'hit':
                    game.hit(current.name)
                elif action == 'stand':
                    game.stand(current.name)
                elif action == 'double_down':
                    game.double_down(current.name)
        
        # ===== COMPLETE PHASE =====
        elif game.phase == GamePhase.COMPLETE:
            print_game_state(game)
            
            action = get_end_round_action()
            
            if action == 'quit':
                print("\n" + "=" * 60)
                print("FINAL STANDINGS:")
                for player in game.player_manager.get_all_players():
                    print(f"   {player.name}: {player.chips} chips")
                print("=" * 60)
                print("Thanks for playing! 👋")
                break
            elif action == 'new_round':
                game.new_round()
            elif action == 'lobby':
                game.back_to_lobby()
        
        # ===== DEALER TURN / DEALING =====
        else:
            # These phases are automatic
            pass


if __name__ == "__main__":
    main()
