"""
Card Representation with Bitmasking.

Uses efficient bit manipulation for fast hand evaluation:
- Rank represented as bit position (2=0, 3=1, ..., A=12)
- Suit represented as one-hot encoding (4 bits)
- Combined bitmask for O(1) flush/straight detection

Example:
    Ace of Spades: rank_bit=12, suit_mask=0b1000
    5 of Hearts:   rank_bit=3,  suit_mask=0b0100
"""

from enum import IntEnum
from typing import List, Optional, Union
from functools import total_ordering


class Rank(IntEnum):
    """Card ranks from 2 (lowest) to Ace (highest)."""
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12
    
    @classmethod
    def from_char(cls, char: str) -> "Rank":
        """Parse rank from character (2-9, T, J, Q, K, A)."""
        char = char.upper()
        mapping = {
            '2': cls.TWO, '3': cls.THREE, '4': cls.FOUR, '5': cls.FIVE,
            '6': cls.SIX, '7': cls.SEVEN, '8': cls.EIGHT, '9': cls.NINE,
            'T': cls.TEN, '10': cls.TEN, 'J': cls.JACK, 'Q': cls.QUEEN,
            'K': cls.KING, 'A': cls.ACE
        }
        if char not in mapping:
            raise ValueError(f"Invalid rank character: {char}")
        return mapping[char]
    
    def to_char(self) -> str:
        """Convert rank to display character."""
        chars = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        return chars[self.value]
    
    def to_name(self) -> str:
        """Convert rank to full name."""
        names = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
                 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']
        return names[self.value]


class Suit(IntEnum):
    """Card suits with one-hot bit encoding."""
    CLUBS = 0     # 0b0001
    DIAMONDS = 1  # 0b0010
    HEARTS = 2    # 0b0100
    SPADES = 3    # 0b1000
    
    @classmethod
    def from_char(cls, char: str) -> "Suit":
        """Parse suit from character (c, d, h, s)."""
        char = char.lower()
        mapping = {
            'c': cls.CLUBS, 'd': cls.DIAMONDS,
            'h': cls.HEARTS, 's': cls.SPADES,
            '♣': cls.CLUBS, '♦': cls.DIAMONDS,
            '♥': cls.HEARTS, '♠': cls.SPADES
        }
        if char not in mapping:
            raise ValueError(f"Invalid suit character: {char}")
        return mapping[char]
    
    def to_char(self) -> str:
        """Convert suit to display character."""
        return ['c', 'd', 'h', 's'][self.value]
    
    def to_symbol(self) -> str:
        """Convert suit to Unicode symbol."""
        return ['♣', '♦', '♥', '♠'][self.value]
    
    def to_name(self) -> str:
        """Convert suit to full name."""
        return ['Clubs', 'Diamonds', 'Hearts', 'Spades'][self.value]
    
    @property
    def bitmask(self) -> int:
        """One-hot bitmask for this suit."""
        return 1 << self.value


# Prime numbers for each rank - used for unique hand identification
# Multiplying primes for each rank gives unique product per combination
RANK_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]


@total_ordering
class Card:
    """
    A playing card with efficient bitmask representation.
    
    The card stores:
    - rank: 0-12 (2 through Ace)
    - suit: 0-3 (Clubs, Diamonds, Hearts, Spades)
    - rank_bit: Bit position for rank (1 << rank)
    - suit_mask: One-hot suit encoding (1 << suit)
    - prime: Prime number for rank (for hash collision-free lookups)
    
    Bitmask Layout (32-bit integer):
        Bits 0-3:   Suit (one-hot)
        Bits 4-7:   Rank value (0-12)
        Bits 16-28: Rank bit pattern (one-hot, for straight detection)
    
    Example:
        >>> card = Card("As")  # Ace of Spades
        >>> card.rank == Rank.ACE
        True
        >>> card.suit_mask == 0b1000
        True
    """
    
    __slots__ = ('rank', 'suit', 'rank_bit', 'suit_mask', 'prime', '_bitmask')
    
    def __init__(self, card_str: Optional[str] = None, 
                 rank: Optional[Rank] = None, 
                 suit: Optional[Suit] = None):
        """
        Create a card from string or rank/suit.
        
        Args:
            card_str: String like "As" (Ace of spades), "Th" (Ten of hearts)
            rank: Rank enum value
            suit: Suit enum value
        """
        if card_str:
            card_str = card_str.strip()
            if len(card_str) == 2:
                rank_char, suit_char = card_str[0], card_str[1]
            elif len(card_str) == 3:  # "10s" format
                rank_char, suit_char = card_str[:2], card_str[2]
            else:
                raise ValueError(f"Invalid card string: {card_str}")
            
            self.rank = Rank.from_char(rank_char)
            self.suit = Suit.from_char(suit_char)
        elif rank is not None and suit is not None:
            self.rank = rank
            self.suit = suit
        else:
            raise ValueError("Must provide card_str or both rank and suit")
        
        # Precompute bitmask components
        self.rank_bit = 1 << self.rank.value
        self.suit_mask = 1 << self.suit.value
        self.prime = RANK_PRIMES[self.rank.value]
        
        # Combined bitmask for fast operations
        # Layout: [rank_bit (13 bits)][padding][rank (4 bits)][suit (4 bits)]
        self._bitmask = (self.rank_bit << 16) | (self.rank.value << 4) | self.suit_mask
    
    @property
    def bitmask(self) -> int:
        """Get combined bitmask for this card."""
        return self._bitmask
    
    @classmethod
    def from_int(cls, index: int) -> "Card":
        """
        Create card from index 0-51.
        
        Index = rank * 4 + suit
        """
        if not 0 <= index < 52:
            raise ValueError(f"Card index must be 0-51, got {index}")
        rank = Rank(index // 4)
        suit = Suit(index % 4)
        return cls(rank=rank, suit=suit)
    
    def to_int(self) -> int:
        """Convert card to index 0-51."""
        return self.rank.value * 4 + self.suit.value
    
    def __str__(self) -> str:
        return f"{self.rank.to_char()}{self.suit.to_char()}"
    
    def __repr__(self) -> str:
        return f"Card('{self}')"
    
    def pretty(self) -> str:
        """Return card with Unicode suit symbol."""
        return f"{self.rank.to_char()}{self.suit.to_symbol()}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other: "Card") -> bool:
        """Compare cards by rank, then suit."""
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.suit < other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))


def parse_cards(cards_str: str) -> List[Card]:
    """
    Parse multiple cards from string.
    
    Accepts formats:
    - "As Kh Qd" (space separated)
    - "AsKhQd" (concatenated 2-char)
    - "As,Kh,Qd" (comma separated)
    
    Example:
        >>> cards = parse_cards("As Ks Qs Js Ts")
        >>> len(cards)
        5
    """
    cards_str = cards_str.strip()
    
    # Try comma-separated
    if ',' in cards_str:
        parts = [p.strip() for p in cards_str.split(',')]
    # Try space-separated
    elif ' ' in cards_str:
        parts = cards_str.split()
    # Try concatenated (2 chars each)
    else:
        parts = [cards_str[i:i+2] for i in range(0, len(cards_str), 2)]
    
    return [Card(p) for p in parts if p]


def cards_to_str(cards: List[Card], pretty: bool = False) -> str:
    """Convert list of cards to string."""
    if pretty:
        return ' '.join(c.pretty() for c in cards)
    return ' '.join(str(c) for c in cards)
