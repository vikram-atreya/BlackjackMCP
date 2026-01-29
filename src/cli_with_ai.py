"""
Mixed Human + AI player command-line interface for Blackjack.
Play alongside AI opponents that use optimal basic strategy.
"""
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_multiplayer import MultiPlayerBlackjack, GamePhase
from ai_advisor import get_advisor, get_advice_for_game_state
from ai_player import AIPlayerStrategy

# AI player names
AI_NAMES = ["🤖 Bot-Alpha", "🤖 Bot-Beta", "🤖 Bot-Gamma", "🤖 Bot-Delta", "🤖 Bot-Epsilon", "🤖 Bot-Zeta"]


# Track which players are AI
ai_player_names = set()


def is_ai_player(name: str) -> bool:
    """Check if a player is an AI."""
    return name in ai_player_names


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
                ai_tag = " [AI]" if is_ai_player(p['name']) else ""
                print(f"   • {p['name']}{ai_tag}: {p['chips']} chips")
        else:
            print("\n   No players at table yet.")
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
            ai_tag = " [AI]" if is_ai_player(p['name']) else ""
            print(f"   • {p['name']}{ai_tag}: {p['chips']} chips | {bet_status}")
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
        
        ai_tag = " [AI]" if is_ai_player(p['name']) else ""
        print(f"\n   {p['name']}{ai_tag}{current}{result}")
        print(f"   💰 {p['chips']} chips | Bet: {p['current_bet']}")
        if p['hand']:
            print(f"   🃏 {', '.join(p['hand'])} (Score: {p['score']})")
    
    # Status message AFTER (for non-COMPLETE phases)
    if game.phase != GamePhase.COMPLETE:
        print("\n" + "-" * 60)
        print(f"📢 {state['message']}")
        print("-" * 60)


def get_player_setup():
    """Get number of human and AI players."""
    print("\n--- GAME SETUP ---")
    
    # Get number of human players
    while True:
        try:
            inp = input("\nHow many human players? (0-4, q to quit): ").strip()
            if inp.lower() == 'q':
                return None, None
            num_humans = int(inp)
            if 0 <= num_humans <= 4:
                break
            print("Please enter a number between 0 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    # Get number of AI players
    while True:
        try:
            max_ai = 6 - num_humans
            inp = input(f"\nHow many AI players? (0-{max_ai}, q to quit): ").strip()
            if inp.lower() == 'q':
                return None, None
            num_ai = int(inp)
            if 0 <= num_ai <= max_ai:
                break
            print(f"Please enter a number between 0 and {max_ai}")
        except ValueError:
            print("Please enter a valid number")
    
    if num_humans == 0 and num_ai == 0:
        print("Need at least one player!")
        return get_player_setup()
    
    # Get human player names
    human_names = []
    for i in range(num_humans):
        while True:
            name = input(f"\nHuman player {i + 1} name: ").strip()
            if name.lower() == 'q':
                return None, None
            if not name:
                print("Please enter a name")
                continue
            if name.lower() in [n.lower() for n in human_names]:
                print(f"{name} already added, choose a different name")
                continue
            human_names.append(name)
            break
    
    # Generate AI player names
    ai_names = AI_NAMES[:num_ai]
    
    return human_names, ai_names


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


def get_player_action(player_name: str, available_actions: list, game=None) -> str:
    """Get player's action choice."""
    action_map = {
        'h': 'hit',
        's': 'stand',
        'd': 'double_down',
        'a': 'advice',
        'q': 'quit'
    }
    
    print(f"\n{player_name}'s turn:")
    if 'hit' in available_actions:
        print("  [H] Hit")
    if 'stand' in available_actions:
        print("  [S] Stand")
    if 'double_down' in available_actions:
        print("  [D] Double Down")
    print("  [A] 🤖 Ask AI Advisor")
    print("  [Q] Quit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice in action_map:
            action = action_map[choice]
            if action == 'quit':
                return 'quit'
            if action == 'advice':
                # Get AI advice
                if game:
                    print("\n🤖 AI Advisor says:")
                    advice = get_advice_for_game_state(game.get_state(), player_name)
                    print(f"   {advice}")
                else:
                    print("\n🤖 AI Advisor unavailable.")
                continue  # Ask for action again after showing advice
            if action in available_actions:
                return action
        print("Invalid choice. Try again.")


def ai_make_decision(game: MultiPlayerBlackjack, player_name: str) -> str:
    """AI player makes a decision by asking LLM."""
    state = game.get_state()
    
    # Find player data
    player_data = None
    for p in state['players']:
        if p['name'] == player_name:
            player_data = p
            break
    
    if not player_data:
        return "stand"
    
    dealer_data = state.get('dealer', {})
    dealer_visible_card = dealer_data.get('hand', ['?'])[0] if dealer_data.get('hand') else '?'
    dealer_score = dealer_data.get('visible_score', 10)
    player_score = player_data.get('score', 0)
    player_hand = player_data.get('hand', [])
    can_double = len(player_hand) == 2 and player_data.get('chips', 0) >= player_data.get('current_bet', 0)
    num_cards = len(player_hand)
    
    print(f"\n   🤖 {player_name} is thinking...")
    time.sleep(0.5)
    
    action, reason = AIPlayerStrategy.decide(
        player_hand=player_hand,
        player_score=player_score, 
        dealer_visible_card=dealer_visible_card,
        dealer_visible_score=dealer_score, 
        can_double=can_double, 
        num_cards=num_cards
    )
    
    print(f"   🤖 {player_name}: {reason}")
    time.sleep(0.5)  # Pause for effect
    
    return action


def get_end_round_action() -> str:
    """Get action after round ends."""
    print("\nWhat next?")
    print("  [N] New Round (same players)")
    print("  [L] Back to Lobby (change players)")
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
    global ai_player_names
    
    print("\n" + "=" * 60)
    print("    🃏 BLACKJACK: HUMAN vs AI 🃏")
    print("=" * 60)
    print("\nPlay against AI opponents using optimal strategy!")
    print("Each player starts with 100 chips.")
    
    # Check AI advisor status
    advisor = get_advisor()
    if advisor.is_available():
        print("🤖 AI Advisor: ENABLED (press [A] during your turn)")
    else:
        print("🤖 AI Advisor: Basic strategy mode")
    
    game = MultiPlayerBlackjack(num_decks=6)
    
    while True:
        # ===== LOBBY PHASE =====
        if game.phase == GamePhase.LOBBY:
            ai_player_names = set()  # Reset AI player tracking
            
            human_names, ai_names = get_player_setup()
            if human_names is None:
                print("\nThanks for playing! 👋")
                break
            
            # Add human players first
            for name in human_names:
                result = game.add_player(name)
                print(f"   {result['message']}")
            
            # Add AI players
            for name in ai_names:
                ai_player_names.add(name)
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
                    if is_ai_player(player.name):
                        # AI bets automatically
                        bet = AIPlayerStrategy.decide_bet(player.chips)
                        print(f"\n   {player.name} bets {bet} chips")
                        time.sleep(0.5)
                        result = game.place_bet(player.name, bet)
                    else:
                        # Human bets
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
                if is_ai_player(current.name):
                    # AI plays automatically
                    action = ai_make_decision(game, current.name)
                    
                    if action == 'hit':
                        result = game.hit(current.name)
                        print(f"   🤖 {current.name} HITS!")
                    elif action == 'stand':
                        result = game.stand(current.name)
                        print(f"   🤖 {current.name} STANDS!")
                    elif action == 'double_down':
                        result = game.double_down(current.name)
                        print(f"   🤖 {current.name} DOUBLES DOWN!")
                    
                    time.sleep(1)  # Pause to let human see
                else:
                    # Human plays
                    actions = game.get_available_actions(current.name)
                    action = get_player_action(current.name, actions, game)
                    
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
                    ai_tag = " [AI]" if is_ai_player(player.name) else ""
                    print(f"   {player.name}{ai_tag}: {player.chips} chips")
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
