"""
Multi-player Blackjack game logic and state management.
Supports multiple players with persistent chip tracking.
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from deck import Deck
from player import Player
from dealer import Dealer


class GamePhase(Enum):
    LOBBY = "lobby"               # Players joining/leaving
    BETTING = "betting"           # Players placing bets
    DEALING = "dealing"           # Initial cards being dealt
    PLAYER_TURN = "player_turn"   # Current player making decisions
    DEALER_TURN = "dealer_turn"   # Dealer playing
    COMPLETE = "complete"         # Round finished, showing results


class GameResult(Enum):
    PLAYER_BLACKJACK = "player_blackjack"  # 3:2 payout
    PLAYER_WIN = "player_win"              # 1:1 payout
    DEALER_WIN = "dealer_win"              # Player loses bet
    PUSH = "push"                          # Tie, bet returned
    PLAYER_BUST = "player_bust"            # Player busted


class PlayerManager:
    """Manages persistent player data across games."""
    
    DEFAULT_CHIPS = 100
    
    def __init__(self):
        self._players: Dict[str, Player] = {}
    
    def get_or_create_player(self, name: str) -> Player:
        """Get existing player or create new one with default chips."""
        name_lower = name.lower().strip()
        
        if name_lower in self._players:
            player = self._players[name_lower]
            # Reset hand state but keep chips
            player.reset_hand()
            return player
        
        # New player
        player = Player(name.strip(), self.DEFAULT_CHIPS)
        self._players[name_lower] = player
        return player
    
    def get_player(self, name: str) -> Optional[Player]:
        """Get player by name if exists."""
        return self._players.get(name.lower().strip())
    
    def player_exists(self, name: str) -> bool:
        """Check if player exists."""
        return name.lower().strip() in self._players
    
    def get_all_players(self) -> List[Player]:
        """Get all registered players."""
        return list(self._players.values())
    
    def reset_player_chips(self, name: str) -> bool:
        """Reset a player's chips to default."""
        player = self.get_player(name)
        if player:
            player.chips = self.DEFAULT_CHIPS
            return True
        return False


class MultiPlayerBlackjack:
    """Multi-player Blackjack game."""
    
    def __init__(self, num_decks: int = 6):
        self.deck = Deck(num_decks)
        self.dealer = Dealer()
        self.player_manager = PlayerManager()
        
        # Current round state
        self.active_players: List[Player] = []  # Players in current round
        self.current_player_idx: int = 0
        self.phase = GamePhase.LOBBY
        self.results: Dict[str, GameResult] = {}  # player_name -> result
        self.message: str = "Welcome! Enter player names to join."
    
    @property
    def current_player(self) -> Optional[Player]:
        """Get the current player whose turn it is."""
        if self.active_players and 0 <= self.current_player_idx < len(self.active_players):
            return self.active_players[self.current_player_idx]
        return None
    
    # ========== LOBBY PHASE ==========
    
    def add_player(self, name: str) -> Dict[str, Any]:
        """Add a player to the current round."""
        if self.phase not in [GamePhase.LOBBY, GamePhase.BETTING]:
            return {"success": False, "message": "Cannot add players during a round."}
        
        name = name.strip()
        if not name:
            return {"success": False, "message": "Please enter a valid name."}
        
        # Check if already in this round
        for p in self.active_players:
            if p.name.lower() == name.lower():
                return {"success": False, "message": f"{name} is already in this round."}
        
        player = self.player_manager.get_or_create_player(name)
        
        if player.chips <= 0:
            return {"success": False, "message": f"{player.name} has no chips! They need to buy in."}
        
        self.active_players.append(player)
        is_new = not self.player_manager.player_exists(name)
        
        msg = f"{player.name} joined! " + (
            f"New player - starting with {player.chips} chips." if is_new 
            else f"Welcome back! You have {player.chips} chips."
        )
        
        return {"success": True, "message": msg, "player": player.get_state()}
    
    def remove_player(self, name: str) -> Dict[str, Any]:
        """Remove a player from the current round (not from manager)."""
        if self.phase not in [GamePhase.LOBBY, GamePhase.BETTING]:
            return {"success": False, "message": "Cannot remove players during a round."}
        
        for i, p in enumerate(self.active_players):
            if p.name.lower() == name.lower().strip():
                self.active_players.pop(i)
                return {"success": True, "message": f"{p.name} left the table."}
        
        return {"success": False, "message": f"Player {name} not found at table."}
    
    def start_betting(self) -> Dict[str, Any]:
        """Move from lobby to betting phase."""
        if self.phase != GamePhase.LOBBY:
            return {"success": False, "message": "Not in lobby phase."}
        
        if len(self.active_players) == 0:
            return {"success": False, "message": "Need at least 1 player to start."}
        
        # Reset all hands for the round
        for player in self.active_players:
            player.reset_hand()
        self.dealer.reset_hand()
        self.results = {}
        
        self.phase = GamePhase.BETTING
        self.message = f"Betting phase - {self.active_players[0].name}, place your bet!"
        
        return {"success": True, "state": self.get_state()}
    
    # ========== BETTING PHASE ==========
    
    def place_bet(self, player_name: str, amount: int) -> Dict[str, Any]:
        """Player places their bet."""
        if self.phase != GamePhase.BETTING:
            return {"success": False, "message": "Not in betting phase."}
        
        player = None
        for p in self.active_players:
            if p.name.lower() == player_name.lower().strip():
                player = p
                break
        
        if not player:
            return {"success": False, "message": f"{player_name} is not at the table."}
        
        if player.current_bet > 0:
            return {"success": False, "message": f"{player.name} has already bet."}
        
        if not player.place_bet(amount):
            return {"success": False, "message": f"Invalid bet. {player.name} has {player.chips} chips."}
        
        # Check if all players have bet
        all_bet = all(p.current_bet > 0 for p in self.active_players)
        
        if all_bet:
            return self._start_dealing()
        else:
            # Find next player who hasn't bet
            for p in self.active_players:
                if p.current_bet == 0:
                    self.message = f"{p.name}, place your bet!"
                    break
        
        return {"success": True, "message": f"{player.name} bet {amount} chips.", "state": self.get_state()}
    
    def _start_dealing(self) -> Dict[str, Any]:
        """Deal initial cards to all players and dealer."""
        self.phase = GamePhase.DEALING
        
        # Deal 2 cards to each player and dealer (alternating)
        for _ in range(2):
            for player in self.active_players:
                player.add_card(self.deck.draw())
            self.dealer.add_card(self.deck.draw())
        
        # Check for blackjacks
        self._check_initial_blackjacks()
        
        # Start player turns
        self.current_player_idx = 0
        self._advance_to_next_active_player()
        
        return {"success": True, "state": self.get_state()}
    
    def _check_initial_blackjacks(self):
        """Check for initial blackjacks."""
        dealer_blackjack = self.dealer.has_blackjack
        
        for player in self.active_players:
            if player.has_blackjack:
                if dealer_blackjack:
                    self.results[player.name] = GameResult.PUSH
                    player.chips += player.current_bet  # Return bet
                else:
                    self.results[player.name] = GameResult.PLAYER_BLACKJACK
                    winnings = int(player.current_bet * 2.5)
                    player.chips += winnings
                player.is_standing = True
            elif dealer_blackjack:
                self.results[player.name] = GameResult.DEALER_WIN
                player.is_standing = True
    
    # ========== PLAYER TURN PHASE ==========
    
    def _advance_to_next_active_player(self):
        """Move to next player who can still act."""
        while self.current_player_idx < len(self.active_players):
            player = self.active_players[self.current_player_idx]
            if not player.is_standing and not player.is_busted and player.name not in self.results:
                self.phase = GamePhase.PLAYER_TURN
                self.message = f"{player.name}'s turn. Score: {player.get_score()}"
                return
            self.current_player_idx += 1
        
        # All players done, dealer's turn
        self._play_dealer_turn()
    
    def hit(self, player_name: str) -> Dict[str, Any]:
        """Current player takes a hit."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Not your turn."}
        
        player = self.current_player
        if not player or player.name.lower() != player_name.lower().strip():
            return {"success": False, "message": f"It's {player.name}'s turn, not {player_name}'s."}
        
        card = self.deck.draw()
        is_busted, score = player.hit(card)
        
        if is_busted:
            self.results[player.name] = GameResult.PLAYER_BUST
            self.message = f"{player.name} busted with {score}!"
            self.current_player_idx += 1
            self._advance_to_next_active_player()
        else:
            self.message = f"{player.name} drew {card}. Score: {score}"
        
        return {"success": True, "card_drawn": str(card), "state": self.get_state()}
    
    def stand(self, player_name: str) -> Dict[str, Any]:
        """Current player stands."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Not your turn."}
        
        player = self.current_player
        if not player or player.name.lower() != player_name.lower().strip():
            return {"success": False, "message": f"It's {player.name}'s turn, not {player_name}'s."}
        
        player.stand()
        self.message = f"{player.name} stands with {player.get_score()}."
        
        self.current_player_idx += 1
        self._advance_to_next_active_player()
        
        return {"success": True, "state": self.get_state()}
    
    def double_down(self, player_name: str) -> Dict[str, Any]:
        """Current player doubles down."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Not your turn."}
        
        player = self.current_player
        if not player or player.name.lower() != player_name.lower().strip():
            return {"success": False, "message": f"It's {player.name}'s turn, not {player_name}'s."}
        
        if len(player.hand) != 2:
            return {"success": False, "message": "Can only double down on initial hand."}
        
        if player.chips < player.current_bet:
            return {"success": False, "message": "Not enough chips to double down."}
        
        card = self.deck.draw()
        is_busted, score = player.double_down(card)
        
        if is_busted:
            self.results[player.name] = GameResult.PLAYER_BUST
            self.message = f"{player.name} doubled down and busted with {score}!"
        else:
            self.message = f"{player.name} doubled down. Drew {card}, score: {score}."
        
        self.current_player_idx += 1
        self._advance_to_next_active_player()
        
        return {"success": True, "card_drawn": str(card), "state": self.get_state()}
    
    # ========== DEALER TURN PHASE ==========
    
    def _play_dealer_turn(self):
        """Dealer plays their turn."""
        self.phase = GamePhase.DEALER_TURN
        
        # Only play if there are players who haven't busted
        active_remaining = [p for p in self.active_players if p.name not in self.results]
        
        if active_remaining:
            self.dealer.play_turn(self.deck)
        
        self._determine_winners()
    
    def _determine_winners(self):
        """Determine winners for all remaining players."""
        dealer_score = self.dealer.get_score()
        dealer_busted = self.dealer.is_busted
        
        for player in self.active_players:
            if player.name in self.results:
                continue  # Already resolved (blackjack, bust, etc.)
            
            player_score = player.get_score()
            
            if dealer_busted:
                self.results[player.name] = GameResult.PLAYER_WIN
                player.chips += player.current_bet * 2
            elif player_score > dealer_score:
                self.results[player.name] = GameResult.PLAYER_WIN
                player.chips += player.current_bet * 2
            elif dealer_score > player_score:
                self.results[player.name] = GameResult.DEALER_WIN
            else:
                self.results[player.name] = GameResult.PUSH
                player.chips += player.current_bet
        
        self.phase = GamePhase.COMPLETE
        self.message = "Round complete! See results below."
    
    # ========== NEW ROUND ==========
    
    def new_round(self) -> Dict[str, Any]:
        """Start a new round with current players."""
        if self.phase != GamePhase.COMPLETE:
            return {"success": False, "message": "Current round not finished."}
        
        # Remove players with no chips
        self.active_players = [p for p in self.active_players if p.chips > 0]
        
        # Reset hands
        for player in self.active_players:
            player.reset_hand()
        self.dealer.reset_hand()
        
        self.results = {}
        self.current_player_idx = 0
        
        if self.active_players:
            self.phase = GamePhase.BETTING
            self.message = f"New round! {self.active_players[0].name}, place your bet!"
        else:
            self.phase = GamePhase.LOBBY
            self.message = "All players are out of chips! Add new players."
        
        return {"success": True, "state": self.get_state()}
    
    def back_to_lobby(self) -> Dict[str, Any]:
        """Return to lobby to add/remove players."""
        if self.phase != GamePhase.COMPLETE:
            return {"success": False, "message": "Finish current round first."}
        
        for player in self.active_players:
            player.reset_hand()
        self.dealer.reset_hand()
        
        self.active_players = []
        self.results = {}
        self.phase = GamePhase.LOBBY
        self.message = "Back in lobby. Add players to start a new game!"
        
        return {"success": True, "state": self.get_state()}
    
    # ========== STATE ==========
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete game state."""
        hide_dealer = self.phase in [GamePhase.PLAYER_TURN, GamePhase.DEALING, GamePhase.BETTING]
        
        state = {
            "phase": self.phase.value,
            "message": self.message,
            "dealer": self.dealer.get_state(hide_hole_card=hide_dealer) if self.dealer.hand else None,
            "players": [p.get_state() for p in self.active_players],
            "current_player": self.current_player.name if self.current_player else None,
            "results": {name: result.value for name, result in self.results.items()},
            "deck_cards_remaining": self.deck.cards_remaining()
        }
        
        return state
    
    def get_available_actions(self, player_name: str = None) -> List[str]:
        """Get available actions for current phase/player."""
        if self.phase == GamePhase.LOBBY:
            return ["add_player", "start_betting"]
        
        elif self.phase == GamePhase.BETTING:
            return ["place_bet", "add_player", "remove_player"]
        
        elif self.phase == GamePhase.PLAYER_TURN:
            player = self.current_player
            if player and (not player_name or player.name.lower() == player_name.lower()):
                actions = ["hit", "stand"]
                if len(player.hand) == 2 and player.chips >= player.current_bet:
                    actions.append("double_down")
                return actions
            return []
        
        elif self.phase == GamePhase.COMPLETE:
            return ["new_round", "back_to_lobby"]
        
        return []
    
    def get_player_summary(self) -> str:
        """Get a summary of all registered players."""
        players = self.player_manager.get_all_players()
        if not players:
            return "No players registered yet."
        
        lines = ["Registered Players:"]
        for p in players:
            lines.append(f"  {p.name}: {p.chips} chips")
        return "\n".join(lines)
