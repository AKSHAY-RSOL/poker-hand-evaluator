"""
Monte Carlo Equity Calculator for Texas Hold'em.

Calculates win probability (equity) by simulating thousands of random
outcomes and counting wins/ties/losses.

The Monte Carlo Method:
1. Remove known cards from deck (hero's hand, board)
2. Randomly deal remaining board cards and opponent hands
3. Evaluate all hands and determine winner
4. Repeat N times (typically 10,000+)
5. Equity = wins / total + (ties / total) / 2

This is the industry-standard method for poker equity calculation,
and demonstrates understanding of probability simulation techniques
commonly used in quantitative finance.
"""

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time
from collections import Counter
from .card import Card, Rank, Suit, cards_to_str
from .deck import Deck, create_full_deck
from .evaluator import HandEvaluator, HandResult


@dataclass
class EquityResult:
    """
    Result of equity calculation.
    
    Attributes:
        wins: Number of simulated wins
        ties: Number of simulated ties
        losses: Number of simulated losses
        total: Total simulations run
        win_pct: Win percentage (0-100)
        tie_pct: Tie percentage (0-100)
        lose_pct: Loss percentage (0-100)
        equity: Total equity (win% + tie%/2) as decimal (0-1)
        time_ms: Time taken in milliseconds
    """
    wins: int
    ties: int
    losses: int
    total: int
    win_pct: float
    tie_pct: float
    lose_pct: float
    equity: float
    time_ms: float
    
    def __str__(self) -> str:
        return (
            f"Equity: {self.equity*100:.2f}% "
            f"(Win: {self.win_pct:.1f}%, Tie: {self.tie_pct:.1f}%, Lose: {self.lose_pct:.1f}%)"
        )
    
    def __repr__(self) -> str:
        return f"EquityResult(equity={self.equity:.4f}, wins={self.wins}, ties={self.ties}, total={self.total})"


class EquityCalculator:
    """
    Monte Carlo equity calculator for Texas Hold'em.
    
    Simulates random outcomes to estimate win probability.
    
    Example:
        >>> hero = [Card("As"), Card("Ks")]  # Hole cards
        >>> board = [Card("2h"), Card("7c"), Card("Js")]  # Flop
        >>> result = EquityCalculator.calculate_equity(hero, board, num_simulations=10000)
        >>> print(result)
        Equity: 64.50% (Win: 61.2%, Tie: 6.6%, Lose: 32.2%)
    """
    
    @staticmethod
    def calculate_equity(
        hero_cards: List[Card],
        board_cards: Optional[List[Card]] = None,
        villain_cards: Optional[List[Card]] = None,
        num_simulations: int = 10000,
        num_opponents: int = 1,
        seed: Optional[int] = None
    ) -> EquityResult:
        """
        Calculate equity using Monte Carlo simulation.
        
        Args:
            hero_cards: Hero's hole cards (2 cards)
            board_cards: Known community cards (0-5 cards)
            villain_cards: Villain's known cards (optional, for specific matchups)
            num_simulations: Number of simulations to run
            num_opponents: Number of opponents (default 1)
            seed: Random seed for reproducibility
            
        Returns:
            EquityResult with win/tie/loss statistics
        """
        start_time = time.time()
        
        if board_cards is None:
            board_cards = []
        
        if len(hero_cards) != 2:
            raise ValueError(f"Hero must have exactly 2 hole cards, got {len(hero_cards)}")
        
        if len(board_cards) > 5:
            raise ValueError(f"Board can have at most 5 cards, got {len(board_cards)}")
        
        # Create random generator
        rng = random.Random(seed)
        
        # Cards needed to complete the board
        cards_needed = 5 - len(board_cards)
        
        # All known cards (remove from deck)
        known_cards = set(c.to_int() for c in hero_cards + board_cards)
        if villain_cards:
            known_cards.update(c.to_int() for c in villain_cards)
        
        # Create deck without known cards
        all_cards = create_full_deck()
        available = [c for c in all_cards if c.to_int() not in known_cards]
        
        wins = 0
        ties = 0
        losses = 0
        
        for _ in range(num_simulations):
            # Shuffle available cards
            rng.shuffle(available)
            
            # Deal remaining board cards
            idx = 0
            runout = available[idx:idx + cards_needed]
            idx += cards_needed
            
            full_board = board_cards + runout
            
            # Hero's full hand (7 cards)
            hero_full = hero_cards + full_board
            hero_result = HandEvaluator.evaluate(hero_full)
            
            # Deal to opponents and evaluate
            best_villain_result = None
            
            for opp in range(num_opponents):
                if villain_cards and opp == 0:
                    # Known villain cards
                    opp_cards = villain_cards
                else:
                    # Random villain cards
                    opp_cards = available[idx:idx + 2]
                    idx += 2
                
                opp_full = list(opp_cards) + full_board
                opp_result = HandEvaluator.evaluate(opp_full)
                
                if best_villain_result is None or opp_result > best_villain_result:
                    best_villain_result = opp_result
            
            # Compare results
            if hero_result > best_villain_result:
                wins += 1
            elif hero_result < best_villain_result:
                losses += 1
            else:
                ties += 1
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        total = num_simulations
        win_pct = (wins / total) * 100
        tie_pct = (ties / total) * 100
        lose_pct = (losses / total) * 100
        equity = (wins + ties / 2) / total
        
        return EquityResult(
            wins=wins,
            ties=ties,
            losses=losses,
            total=total,
            win_pct=win_pct,
            tie_pct=tie_pct,
            lose_pct=lose_pct,
            equity=equity,
            time_ms=elapsed_ms
        )
    
    @staticmethod
    def calculate_matchup(
        hand1: List[Card],
        hand2: List[Card],
        board: Optional[List[Card]] = None,
        num_simulations: int = 10000,
        seed: Optional[int] = None
    ) -> Tuple[EquityResult, EquityResult]:
        """
        Calculate equity for a specific matchup between two known hands.
        
        Args:
            hand1: First player's hole cards
            hand2: Second player's hole cards
            board: Known community cards
            num_simulations: Number of simulations
            seed: Random seed
            
        Returns:
            Tuple of (hand1_equity, hand2_equity)
        """
        start_time = time.time()
        
        if board is None:
            board = []
        
        rng = random.Random(seed)
        
        cards_needed = 5 - len(board)
        
        # Remove known cards
        known = set(c.to_int() for c in hand1 + hand2 + board)
        available = [c for c in create_full_deck() if c.to_int() not in known]
        
        wins1, wins2, ties = 0, 0, 0
        
        for _ in range(num_simulations):
            rng.shuffle(available)
            
            full_board = board + available[:cards_needed]
            
            result1 = HandEvaluator.evaluate(hand1 + full_board)
            result2 = HandEvaluator.evaluate(hand2 + full_board)
            
            if result1 > result2:
                wins1 += 1
            elif result2 > result1:
                wins2 += 1
            else:
                ties += 1
        
        elapsed = (time.time() - start_time) * 1000
        
        total = num_simulations
        
        equity1 = EquityResult(
            wins=wins1, ties=ties, losses=wins2, total=total,
            win_pct=wins1/total*100, tie_pct=ties/total*100, lose_pct=wins2/total*100,
            equity=(wins1 + ties/2) / total, time_ms=elapsed
        )
        
        equity2 = EquityResult(
            wins=wins2, ties=ties, losses=wins1, total=total,
            win_pct=wins2/total*100, tie_pct=ties/total*100, lose_pct=wins1/total*100,
            equity=(wins2 + ties/2) / total, time_ms=elapsed
        )
        
        return equity1, equity2
    
    @staticmethod
    def preflop_equity(
        hand: List[Card],
        num_simulations: int = 10000,
        num_opponents: int = 1,
        seed: Optional[int] = None
    ) -> EquityResult:
        """
        Calculate preflop equity (no board cards yet).
        
        Args:
            hand: Hero's hole cards
            num_simulations: Number of simulations
            num_opponents: Number of random opponents
            seed: Random seed
            
        Returns:
            EquityResult
        """
        return EquityCalculator.calculate_equity(
            hero_cards=hand,
            board_cards=[],
            num_simulations=num_simulations,
            num_opponents=num_opponents,
            seed=seed
        )


def calculate_equity(hero: List[Card], board: List[Card] = None, 
                    simulations: int = 10000) -> float:
    """Convenience function returning equity as percentage."""
    result = EquityCalculator.calculate_equity(
        hero_cards=hero,
        board_cards=board or [],
        num_simulations=simulations
    )
    return result.equity * 100


# Common preflop hand equities (approximate, vs 1 random hand)
PREFLOP_EQUITY_TABLE = {
    "AA": 85.0, "KK": 82.0, "QQ": 80.0, "JJ": 77.5, "TT": 75.0,
    "99": 72.0, "88": 69.0, "77": 66.0, "66": 63.0, "55": 60.0,
    "AKs": 67.0, "AKo": 65.0, "AQs": 66.0, "AQo": 64.0,
    "KQs": 63.0, "KQo": 60.0, "JTs": 57.0, "T9s": 54.0,
}
