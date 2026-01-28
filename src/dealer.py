"""
Dealer class for Blackjack game.
Implements dealer logic - must hit on 16 or less, stand on 17+.
"""
from typing import List, Tuple
from deck import Card, Deck


class Dealer:
    def __init__(self):
        self.hand: List[Card] = []
        self.is_standing: bool = False
        self.is_busted: bool = False
        self.has_blackjack: bool = False
    
    def reset_hand(self) -> None:
        """Reset dealer's hand for a new round."""
        self.hand = []
        self.is_standing = False
        self.is_busted = False
        self.has_blackjack = False
    
    def add_card(self, card: Card) -> None:
        """Add a card to dealer's hand."""
        self.hand.append(card)
        self._check_status()
    
    def _check_status(self) -> None:
        """Check if dealer has blackjack or busted."""
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
        
        # Convert aces from 11 to 1 as needed
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    def get_visible_card(self) -> Card:
        """Get the dealer's face-up card (first card)."""
        return self.hand[0] if self.hand else None
    
    def should_hit(self) -> bool:
        """
        Dealer must hit on 16 or less, stand on 17+.
        Some variants have dealer hit on soft 17 - can be configured.
        """
        return self.get_score() < 17
    
    def play_turn(self, deck: Deck) -> List[Card]:
        """
        Dealer plays their turn automatically.
        Returns list of cards drawn.
        """
        cards_drawn = []
        
        while self.should_hit() and not self.is_busted:
            card = deck.draw()
            self.add_card(card)
            cards_drawn.append(card)
        
        if not self.is_busted:
            self.is_standing = True
        
        return cards_drawn
    
    def get_hand_str(self, hide_second: bool = False) -> str:
        """
        Get string representation of hand.
        If hide_second=True, shows only the first card (during player's turn).
        """
        if not self.hand:
            return "No cards"
        
        if hide_second and len(self.hand) >= 2:
            return f"{self.hand[0]}, [Hidden]"
        
        return ", ".join(str(card) for card in self.hand)
    
    def get_state(self, hide_hole_card: bool = False) -> dict:
        """
        Get dealer state as dictionary.
        If hide_hole_card=True, only shows first card.
        """
        if hide_hole_card and len(self.hand) >= 2:
            return {
                "hand": [str(self.hand[0]), "Hidden"],
                "visible_score": self.hand[0].value,
                "is_standing": self.is_standing,
                "is_busted": False,
                "has_blackjack": False  # Don't reveal yet
            }
        
        return {
            "hand": [str(card) for card in self.hand],
            "score": self.get_score(),
            "is_standing": self.is_standing,
            "is_busted": self.is_busted,
            "has_blackjack": self.has_blackjack
        }
