"""
Deck Management for Poker.

Provides efficient deck operations:
- Standard 52-card deck creation
- Fast shuffling
- Drawing cards
- Removing known cards (for equity calculations)
"""

import random
from typing import List, Set, Optional, Iterable
from .card import Card, Rank, Suit


class Deck:
    """
    A standard 52-card deck.
    
    Supports:
    - Shuffling with custom random state
    - Drawing cards
    - Removing specific cards (dead cards)
    - Reset to full deck
    
    Example:
        >>> deck = Deck()
        >>> deck.shuffle()
        >>> hand = deck.draw(2)
        >>> len(deck)
        50
    """
    
    def __init__(self, exclude: Optional[Iterable[Card]] = None):
        """
        Create a deck, optionally excluding certain cards.
        
        Args:
            exclude: Cards to exclude from the deck (e.g., known cards)
        """
        self._all_cards = [
            Card(rank=rank, suit=suit)
            for rank in Rank
            for suit in Suit
        ]
        
        self._excluded: Set[int] = set()
        if exclude:
            for card in exclude:
                self._excluded.add(card.to_int())
        
        self._cards: List[Card] = []
        self.reset()
    
    def reset(self) -> None:
        """Reset deck to all cards (minus excluded)."""
        self._cards = [
            card for card in self._all_cards
            if card.to_int() not in self._excluded
        ]
    
    def shuffle(self, rng: Optional[random.Random] = None) -> None:
        """
        Shuffle the deck.
        
        Args:
            rng: Optional random number generator for reproducibility
        """
        if rng:
            rng.shuffle(self._cards)
        else:
            random.shuffle(self._cards)
    
    def draw(self, n: int = 1) -> List[Card]:
        """
        Draw n cards from the deck.
        
        Args:
            n: Number of cards to draw
            
        Returns:
            List of drawn cards
            
        Raises:
            ValueError: If not enough cards remaining
        """
        if n > len(self._cards):
            raise ValueError(f"Cannot draw {n} cards, only {len(self._cards)} remaining")
        
        drawn = self._cards[:n]
        self._cards = self._cards[n:]
        return drawn
    
    def draw_one(self) -> Card:
        """Draw a single card."""
        return self.draw(1)[0]
    
    def remove(self, cards: Iterable[Card]) -> None:
        """Remove specific cards from the deck."""
        to_remove = {card.to_int() for card in cards}
        self._cards = [c for c in self._cards if c.to_int() not in to_remove]
    
    def peek(self, n: int = 1) -> List[Card]:
        """Look at top n cards without removing them."""
        return self._cards[:n]
    
    @property
    def remaining(self) -> List[Card]:
        """Get all remaining cards (without drawing)."""
        return self._cards.copy()
    
    def __len__(self) -> int:
        return len(self._cards)
    
    def __iter__(self):
        return iter(self._cards)
    
    def __repr__(self) -> str:
        return f"Deck({len(self._cards)} cards)"


def create_full_deck() -> List[Card]:
    """Create a list of all 52 cards."""
    return [
        Card(rank=rank, suit=suit)
        for rank in Rank
        for suit in Suit
    ]
