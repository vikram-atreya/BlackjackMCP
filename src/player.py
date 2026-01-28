"""
Player class for Blackjack game.
Handles player hand, actions, and betting.
"""
from typing import List, Tuple
from deck import Card


class Player:
    def __init__(self, name: str = "Player", chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.current_bet: int = 0
        self.is_standing: bool = False
        self.is_busted: bool = False
        self.has_blackjack: bool = False
    
    def reset_hand(self) -> None:
        """Reset player's hand for a new round."""
        self.hand = []
        self.current_bet = 0
        self.is_standing = False
        self.is_busted = False
        self.has_blackjack = False
    
    def add_card(self, card: Card) -> None:
        """Add a card to player's hand."""
        self.hand.append(card)
        self._check_status()
    
    def _check_status(self) -> None:
        """Check if player has blackjack or busted."""
        score = self.get_score()
        if score > 21:
            self.is_busted = True
        elif score == 21 and len(self.hand) == 2:
            self.has_blackjack = True
    
    def get_score(self) -> int:
        """
        Calculate the best score for the hand.
        Handles soft/hard aces automatically.
        """
        score = sum(card.value for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == 'A')
        
        # Convert aces from 11 to 1 as needed to avoid busting
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    def place_bet(self, amount: int) -> bool:
        """Place a bet. Returns True if successful."""
        if amount <= 0 or amount > self.chips:
            return False
        self.current_bet = amount
        self.chips -= amount
        return True
    
    def hit(self, card: Card) -> Tuple[bool, int]:
        """
        Player takes a hit.
        Returns (is_busted, new_score).
        """
        self.add_card(card)
        return (self.is_busted, self.get_score())
    
    def stand(self) -> None:
        """Player stands."""
        self.is_standing = True
    
    def double_down(self, card: Card) -> Tuple[bool, int]:
        """
        Double down - double bet, take one card, then stand.
        Returns (is_busted, new_score).
        """
        if self.chips >= self.current_bet:
            self.chips -= self.current_bet
            self.current_bet *= 2
        
        self.add_card(card)
        self.is_standing = True
        return (self.is_busted, self.get_score())
    
    def get_hand_str(self) -> str:
        """Get string representation of hand."""
        return ", ".join(str(card) for card in self.hand)
    
    def get_state(self) -> dict:
        """Get player state as dictionary."""
        return {
            "name": self.name,
            "chips": self.chips,
            "hand": [str(card) for card in self.hand],
            "score": self.get_score(),
            "current_bet": self.current_bet,
            "is_standing": self.is_standing,
            "is_busted": self.is_busted,
            "has_blackjack": self.has_blackjack
        }
