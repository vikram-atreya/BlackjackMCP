"""
Deck and Card classes for Blackjack game.
"""
import random
from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    suit: str  # Hearts, Diamonds, Clubs, Spades
    rank: str  # 2-10, J, Q, K, A
    
    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"
    
    @property
    def value(self) -> int:
        """Returns the blackjack value of the card. Ace returns 11 (high value)."""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Caller handles soft/hard ace logic
        else:
            return int(self.rank)


class Deck:
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, num_decks: int = 1):
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self) -> None:
        """Reset and shuffle the deck."""
        self.cards = [
            Card(suit, rank)
            for _ in range(self.num_decks)
            for suit in self.SUITS
            for rank in self.RANKS
        ]
        self.shuffle()
    
    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def draw(self) -> Card:
        """Draw a card from the deck."""
        if not self.cards:
            self.reset()  # Auto-reshuffle if empty
        return self.cards.pop()
    
    def cards_remaining(self) -> int:
        """Return number of cards remaining."""
        return len(self.cards)
