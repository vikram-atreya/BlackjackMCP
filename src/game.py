"""
Core Blackjack game logic and state management.
Orchestrates player, dealer, and deck interactions.
"""
from enum import Enum
from typing import Optional, Dict, Any
from deck import Deck
from player import Player
from dealer import Dealer


class GamePhase(Enum):
    WAITING = "waiting"           # Waiting for bet
    DEALING = "dealing"           # Initial cards being dealt
    PLAYER_TURN = "player_turn"   # Player making decisions
    DEALER_TURN = "dealer_turn"   # Dealer playing
    COMPLETE = "complete"         # Round finished


class GameResult(Enum):
    PLAYER_BLACKJACK = "player_blackjack"  # 3:2 payout
    PLAYER_WIN = "player_win"              # 1:1 payout
    DEALER_WIN = "dealer_win"              # Player loses bet
    PUSH = "push"                          # Tie, bet returned
    PLAYER_BUST = "player_bust"            # Player busted


class BlackjackGame:
    def __init__(self, num_decks: int = 6, player_name: str = "Player", starting_chips: int = 1000):
        self.deck = Deck(num_decks)
        self.player = Player(player_name, starting_chips)
        self.dealer = Dealer()
        self.phase = GamePhase.WAITING
        self.result: Optional[GameResult] = None
        self.message: str = "Place your bet to start!"
    
    def place_bet(self, amount: int) -> Dict[str, Any]:
        """Place a bet and start a new round."""
        if self.phase != GamePhase.WAITING:
            return {"success": False, "message": "Cannot bet now. Finish current round first."}
        
        # Reset hands FIRST, then place bet, then deal
        self.player.reset_hand()
        self.dealer.reset_hand()
        
        if not self.player.place_bet(amount):
            return {"success": False, "message": f"Invalid bet. You have {self.player.chips} chips."}
        
        # Deal initial cards
        self._deal_initial_cards()
        
        # Check for blackjacks
        if self.player.has_blackjack:
            if self.dealer.has_blackjack:
                self._end_round(GameResult.PUSH, "Both have Blackjack! Push.")
            else:
                self._end_round(GameResult.PLAYER_BLACKJACK, "Blackjack! You win 3:2!")
        elif self.dealer.has_blackjack:
            self._end_round(GameResult.DEALER_WIN, "Dealer has Blackjack. You lose.")
        else:
            self.phase = GamePhase.PLAYER_TURN
            self.message = "Your turn. Hit, Stand, or Double Down?"
        
        return {"success": True, "state": self.get_state()}
    
    def _deal_initial_cards(self) -> None:
        """Deal initial 2 cards each to player and dealer."""
        self.phase = GamePhase.DEALING
        self.result = None
        
        # Deal alternating: player, dealer, player, dealer
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
    
    def hit(self) -> Dict[str, Any]:
        """Player takes a hit."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Cannot hit now."}
        
        card = self.deck.draw()
        is_busted, score = self.player.hit(card)
        
        if is_busted:
            self._end_round(GameResult.PLAYER_BUST, f"Busted with {score}! You lose.")
        else:
            self.message = f"Drew {card}. Score: {score}. Hit, Stand?"
        
        return {"success": True, "card_drawn": str(card), "state": self.get_state()}
    
    def stand(self) -> Dict[str, Any]:
        """Player stands."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Cannot stand now."}
        
        self.player.stand()
        self._play_dealer_turn()
        
        return {"success": True, "state": self.get_state()}
    
    def double_down(self) -> Dict[str, Any]:
        """Player doubles down."""
        if self.phase != GamePhase.PLAYER_TURN:
            return {"success": False, "message": "Cannot double down now."}
        
        if len(self.player.hand) != 2:
            return {"success": False, "message": "Can only double down on initial hand."}
        
        if self.player.chips < self.player.current_bet:
            return {"success": False, "message": "Not enough chips to double down."}
        
        card = self.deck.draw()
        is_busted, score = self.player.double_down(card)
        
        if is_busted:
            self._end_round(GameResult.PLAYER_BUST, f"Busted with {score}! You lose.")
        else:
            self._play_dealer_turn()
        
        return {"success": True, "card_drawn": str(card), "state": self.get_state()}
    
    def _play_dealer_turn(self) -> None:
        """Dealer plays their turn."""
        self.phase = GamePhase.DEALER_TURN
        
        cards_drawn = self.dealer.play_turn(self.deck)
        
        self._determine_winner()
    
    def _determine_winner(self) -> None:
        """Determine the winner after dealer's turn."""
        player_score = self.player.get_score()
        dealer_score = self.dealer.get_score()
        
        if self.dealer.is_busted:
            self._end_round(GameResult.PLAYER_WIN, f"Dealer busts with {dealer_score}! You win!")
        elif player_score > dealer_score:
            self._end_round(GameResult.PLAYER_WIN, f"You win! {player_score} vs {dealer_score}")
        elif dealer_score > player_score:
            self._end_round(GameResult.DEALER_WIN, f"Dealer wins. {dealer_score} vs {player_score}")
        else:
            self._end_round(GameResult.PUSH, f"Push! Both have {player_score}")
    
    def _end_round(self, result: GameResult, message: str) -> None:
        """End the round and handle payouts."""
        self.phase = GamePhase.COMPLETE
        self.result = result
        bet = self.player.current_bet
        
        # Handle payouts
        if result == GameResult.PLAYER_BLACKJACK:
            winnings = int(bet * 2.5)  # 3:2 payout (bet + 1.5x bet)
            self.player.chips += winnings
            message += f" Won {winnings} chips."
        elif result == GameResult.PLAYER_WIN:
            winnings = bet * 2  # 1:1 payout (bet + 1x bet)
            self.player.chips += winnings
            message += f" Won {winnings} chips."
        elif result == GameResult.PUSH:
            self.player.chips += bet  # Return bet
            message += " Bet returned."
        # DEALER_WIN and PLAYER_BUST: bet already deducted
        
        self.message = message
    
    def new_round(self) -> Dict[str, Any]:
        """Start a new round (reset for betting)."""
        if self.phase != GamePhase.COMPLETE:
            return {"success": False, "message": "Current round not finished."}
        
        self.player.reset_hand()
        self.dealer.reset_hand()
        self.phase = GamePhase.WAITING
        self.result = None
        self.message = "Place your bet to start!"
        
        return {"success": True, "state": self.get_state()}
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete game state."""
        hide_dealer = self.phase in [GamePhase.PLAYER_TURN, GamePhase.DEALING]
        
        return {
            "phase": self.phase.value,
            "result": self.result.value if self.result else None,
            "message": self.message,
            "player": self.player.get_state(),
            "dealer": self.dealer.get_state(hide_hole_card=hide_dealer),
            "deck_cards_remaining": self.deck.cards_remaining()
        }
    
    def get_available_actions(self) -> list:
        """Get list of available actions in current phase."""
        if self.phase == GamePhase.WAITING:
            return ["place_bet"]
        elif self.phase == GamePhase.PLAYER_TURN:
            actions = ["hit", "stand"]
            if len(self.player.hand) == 2 and self.player.chips >= self.player.current_bet:
                actions.append("double_down")
            return actions
        elif self.phase == GamePhase.COMPLETE:
            return ["new_round"]
        return []
