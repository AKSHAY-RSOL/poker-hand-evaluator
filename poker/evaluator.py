"""
Poker Hand Evaluator using Bitmasking.

Evaluates poker hands efficiently using bit manipulation:
- Flush detection: O(1) via suit bitmask comparison
- Straight detection: O(1) via rank bitmask pattern matching
- Hand ranking: O(1) lookup after classification

Supports 5-7 card evaluation (Texas Hold'em).

Hand Rankings (best to worst):
1. Royal Flush     - A K Q J T of same suit
2. Straight Flush  - 5 consecutive cards of same suit
3. Four of a Kind  - 4 cards of same rank
4. Full House      - 3 of a kind + pair
5. Flush           - 5 cards of same suit
6. Straight        - 5 consecutive ranks
7. Three of a Kind - 3 cards of same rank
8. Two Pair        - 2 different pairs
9. One Pair        - 2 cards of same rank
10. High Card      - Highest card wins
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Tuple, Optional
from itertools import combinations
from collections import Counter
from .card import Card, Rank


class HandRank(IntEnum):
    """
    Hand ranking categories.
    
    Higher value = better hand.
    """
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10
    
    def __str__(self) -> str:
        names = {
            HandRank.HIGH_CARD: "High Card",
            HandRank.ONE_PAIR: "One Pair",
            HandRank.TWO_PAIR: "Two Pair",
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush",
        }
        return names[self]


@dataclass
class HandResult:
    """
    Result of hand evaluation.
    
    Attributes:
        rank: The hand category (e.g., FLUSH, FULL_HOUSE)
        strength: Numeric strength for comparison (higher = better)
        cards: The 5 cards making up the best hand
        kickers: Kicker cards used for tiebreaking
        description: Human-readable description
    """
    rank: HandRank
    strength: int
    cards: List[Card]
    kickers: Tuple[int, ...]
    description: str
    
    def __lt__(self, other: "HandResult") -> bool:
        return self.strength < other.strength
    
    def __le__(self, other: "HandResult") -> bool:
        return self.strength <= other.strength
    
    def __gt__(self, other: "HandResult") -> bool:
        return self.strength > other.strength
    
    def __ge__(self, other: "HandResult") -> bool:
        return self.strength >= other.strength
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, HandResult):
            return False
        return self.strength == other.strength
    
    def __repr__(self) -> str:
        cards_str = ' '.join(c.pretty() for c in self.cards)
        return f"HandResult({self.rank}: {cards_str})"


# Straight patterns as bitmasks
# Each bit represents a rank: bit 0 = 2, bit 12 = Ace
# Ace-low straight (A2345) has Ace at bit 12 AND bits 0-3
STRAIGHT_PATTERNS = [
    0b1111100000000,  # AKQJT (Royal/Broadway)
    0b0111110000000,  # KQJT9
    0b0011111000000,  # QJT98
    0b0001111100000,  # JT987
    0b0000111110000,  # T9876
    0b0000011111000,  # 98765
    0b0000001111100,  # 87654
    0b0000000111110,  # 76543
    0b0000000011111,  # 65432
    0b1000000001111,  # A2345 (Wheel) - Ace high bit + 2345
]

# High card of each straight pattern
STRAIGHT_HIGH_CARDS = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3]  # A, K, Q, J, T, 9, 8, 7, 6, 5


class HandEvaluator:
    """
    Evaluates poker hands using efficient bit manipulation.
    
    Key optimizations:
    - Flush detection via suit bitmask (single AND operation)
    - Straight detection via rank pattern matching
    - Precomputed lookup tables for common patterns
    
    Example:
        >>> cards = [Card("As"), Card("Ks"), Card("Qs"), Card("Js"), Card("Ts")]
        >>> result = HandEvaluator.evaluate(cards)
        >>> result.rank == HandRank.ROYAL_FLUSH
        True
    """
    
    @staticmethod
    def evaluate(cards: List[Card]) -> HandResult:
        """
        Evaluate a poker hand.
        
        Args:
            cards: 5-7 cards to evaluate
            
        Returns:
            HandResult with rank, strength, and description
        """
        if len(cards) < 5:
            raise ValueError(f"Need at least 5 cards, got {len(cards)}")
        
        if len(cards) == 5:
            return HandEvaluator._evaluate_5(cards)
        
        # For 6-7 cards, find best 5-card combination
        best_result = None
        for combo in combinations(cards, 5):
            result = HandEvaluator._evaluate_5(list(combo))
            if best_result is None or result > best_result:
                best_result = result
        
        return best_result
    
    @staticmethod
    def _evaluate_5(cards: List[Card]) -> HandResult:
        """Evaluate exactly 5 cards."""
        # Extract rank and suit information
        ranks = [c.rank.value for c in cards]
        suits = [c.suit.value for c in cards]
        
        # Create rank bitmask (one bit per rank present)
        rank_mask = 0
        for r in ranks:
            rank_mask |= (1 << r)
        
        # Count ranks for pair/trips/quads detection
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Sort ranks by count (descending), then by rank (descending)
        sorted_ranks = sorted(
            rank_counts.keys(),
            key=lambda r: (rank_counts[r], r),
            reverse=True
        )
        
        # Check for flush (all same suit)
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight, straight_high = HandEvaluator._check_straight(rank_mask)
        
        # Determine hand category
        if is_straight and is_flush:
            if straight_high == 12:  # Ace-high straight flush
                rank = HandRank.ROYAL_FLUSH
                desc = "Royal Flush"
            else:
                rank = HandRank.STRAIGHT_FLUSH
                high_name = Rank(straight_high).to_name()
                desc = f"Straight Flush, {high_name} high"
            
            strength = HandEvaluator._make_strength(rank, (straight_high,))
            kickers = (straight_high,)
        
        elif counts == [4, 1]:  # Four of a kind
            rank = HandRank.FOUR_OF_A_KIND
            quad_rank = sorted_ranks[0]
            kicker = sorted_ranks[1]
            desc = f"Four of a Kind, {Rank(quad_rank).to_name()}s"
            strength = HandEvaluator._make_strength(rank, (quad_rank, kicker))
            kickers = (quad_rank, kicker)
        
        elif counts == [3, 2]:  # Full house
            rank = HandRank.FULL_HOUSE
            trip_rank = sorted_ranks[0]
            pair_rank = sorted_ranks[1]
            desc = f"Full House, {Rank(trip_rank).to_name()}s full of {Rank(pair_rank).to_name()}s"
            strength = HandEvaluator._make_strength(rank, (trip_rank, pair_rank))
            kickers = (trip_rank, pair_rank)
        
        elif is_flush:
            rank = HandRank.FLUSH
            sorted_flush = tuple(sorted(ranks, reverse=True))
            desc = f"Flush, {Rank(sorted_flush[0]).to_name()} high"
            strength = HandEvaluator._make_strength(rank, sorted_flush)
            kickers = sorted_flush
        
        elif is_straight:
            rank = HandRank.STRAIGHT
            high_name = Rank(straight_high).to_name()
            desc = f"Straight, {high_name} high"
            strength = HandEvaluator._make_strength(rank, (straight_high,))
            kickers = (straight_high,)
        
        elif counts == [3, 1, 1]:  # Three of a kind
            rank = HandRank.THREE_OF_A_KIND
            trip_rank = sorted_ranks[0]
            kicker_ranks = tuple(sorted(sorted_ranks[1:], reverse=True))
            desc = f"Three of a Kind, {Rank(trip_rank).to_name()}s"
            strength = HandEvaluator._make_strength(rank, (trip_rank,) + kicker_ranks)
            kickers = (trip_rank,) + kicker_ranks
        
        elif counts == [2, 2, 1]:  # Two pair
            rank = HandRank.TWO_PAIR
            pairs = sorted([sorted_ranks[0], sorted_ranks[1]], reverse=True)
            kicker = sorted_ranks[2]
            desc = f"Two Pair, {Rank(pairs[0]).to_name()}s and {Rank(pairs[1]).to_name()}s"
            strength = HandEvaluator._make_strength(rank, (pairs[0], pairs[1], kicker))
            kickers = (pairs[0], pairs[1], kicker)
        
        elif counts == [2, 1, 1, 1]:  # One pair
            rank = HandRank.ONE_PAIR
            pair_rank = sorted_ranks[0]
            kicker_ranks = tuple(sorted(sorted_ranks[1:], reverse=True))
            desc = f"One Pair, {Rank(pair_rank).to_name()}s"
            strength = HandEvaluator._make_strength(rank, (pair_rank,) + kicker_ranks)
            kickers = (pair_rank,) + kicker_ranks
        
        else:  # High card
            rank = HandRank.HIGH_CARD
            sorted_high = tuple(sorted(ranks, reverse=True))
            desc = f"High Card, {Rank(sorted_high[0]).to_name()}"
            strength = HandEvaluator._make_strength(rank, sorted_high)
            kickers = sorted_high
        
        return HandResult(
            rank=rank,
            strength=strength,
            cards=sorted(cards, key=lambda c: c.rank, reverse=True),
            kickers=kickers,
            description=desc
        )
    
    @staticmethod
    def _check_straight(rank_mask: int) -> Tuple[bool, int]:
        """
        Check if rank bitmask forms a straight.
        
        Uses precomputed straight patterns for O(1) detection.
        
        Returns:
            (is_straight, high_card_rank) or (False, 0)
        """
        for pattern, high in zip(STRAIGHT_PATTERNS, STRAIGHT_HIGH_CARDS):
            if pattern == 0b1000000001111:  # Ace-low straight (wheel)
                # Check for A,2,3,4,5 specifically
                if (rank_mask & 0b1000000001111) == 0b1000000001111:
                    # Make sure we have exactly 5 unique ranks
                    if bin(rank_mask).count('1') == 5:
                        return True, high
            elif (rank_mask & pattern) == pattern:
                # Make sure we have exactly these 5 cards
                if bin(rank_mask).count('1') == 5:
                    return True, high
        
        return False, 0
    
    @staticmethod
    def _make_strength(rank: HandRank, kickers: Tuple[int, ...]) -> int:
        """
        Create numeric strength for hand comparison.
        
        Format: rank * 10^10 + kicker1 * 10^8 + kicker2 * 10^6 + ...
        
        This ensures hands are compared first by category,
        then by kickers in order.
        """
        strength = rank.value * (10 ** 10)
        for i, kicker in enumerate(kickers[:5]):
            strength += kicker * (10 ** (8 - i * 2))
        return strength
    
    @staticmethod
    def compare_hands(hand1: List[Card], hand2: List[Card]) -> int:
        """
        Compare two hands.
        
        Returns:
            1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        result1 = HandEvaluator.evaluate(hand1)
        result2 = HandEvaluator.evaluate(hand2)
        
        if result1 > result2:
            return 1
        elif result1 < result2:
            return -1
        return 0


def get_hand_strength(cards: List[Card]) -> HandResult:
    """Convenience function for hand evaluation."""
    return HandEvaluator.evaluate(cards)


def rank_hand(cards: List[Card]) -> str:
    """Get human-readable hand description."""
    return HandEvaluator.evaluate(cards).description
