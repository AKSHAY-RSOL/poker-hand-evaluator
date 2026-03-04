# Poker Hand Evaluator & Equity Calculator

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A high-performance Texas Hold'em poker hand evaluator and **Monte Carlo equity calculator** using **bitmasking** for O(1) flush/straight detection.

> Built to demonstrate probabilistic reasoning and bit manipulation techniques.

## Overview

This project demonstrates:
1. **Bitwise Card Representation** - Cards encoded as integers for O(1) flush detection
2. **Hand Strength Evaluation** - Complete poker hand ranking from Royal Flush to High Card
3. **Monte Carlo Simulation** - Calculate win probability (equity) against random hands

## Key Features

### Bitmasking for Speed
Cards are represented as 32-bit integers combining suit and rank information:
- Bits 0-12: Rank bitmask (2-Ace)
- Bits 13-15: Suit encoding
- Flush detection: Single bitwise AND operation
- Straight detection: Bit manipulation with prime product lookup

### Hand Rankings (Best to Worst)
1. Royal Flush
2. Straight Flush
3. Four of a Kind
4. Full House
5. Flush
6. Straight
7. Three of a Kind
8. Two Pair
9. One Pair
10. High Card

### Monte Carlo Equity Calculator
- Simulates thousands of random runouts
- Calculates win/tie/loss percentages
- Supports Texas Hold'em with community cards
- Vectorized operations with NumPy for performance

## Project Structure

```
poker_evaluator/
├── README.md
├── poker/
│   ├── __init__.py
│   ├── card.py           # Bitmask card representation
│   ├── deck.py           # Deck management
│   ├── evaluator.py      # Hand strength evaluation
│   └── equity.py         # Monte Carlo equity calculator
├── tests/
│   └── test_poker.py
└── demo.py
```

## Usage

### Evaluate a Hand
```python
from poker import Card, HandEvaluator

cards = [
    Card("As"), Card("Ks"), Card("Qs"), Card("Js"), Card("Ts")
]
result = HandEvaluator.evaluate(cards)
print(result)  # HandRank.ROYAL_FLUSH
```

### Calculate Equity (Win Probability)
```python
from poker import Card, EquityCalculator

# Your hole cards
hero = [Card("As"), Card("Ks")]

# Community cards (flop)
board = [Card("2h"), Card("7c"), Card("Js")]

# Calculate equity vs random hand
equity = EquityCalculator.calculate_equity(hero, board, num_simulations=10000)
print(f"Win: {equity.win_pct:.1f}%, Tie: {equity.tie_pct:.1f}%")
```

## Performance

| Operation | Time |
|-----------|------|
| Single hand evaluation | ~2 μs |
| 10,000 equity simulations | ~200 ms |

## Why This Matters for Trading

Jane Street uses poker as a training tool because both involve:
- **Incomplete Information**: You don't know opponent's cards/positions
- **Expected Value Calculations**: Equity ≈ EV of a trade
- **Range Thinking**: Opponent could have many possible hands
- **Risk Management**: Pot odds ≈ position sizing

## Technical Highlights

- **Bitmask Operations**: O(1) flush and straight detection
- **Monte Carlo Method**: Industry-standard probability estimation
- **Clean Architecture**: Modular design with type hints
- **Comprehensive Testing**: Edge cases and statistical validation

## Author

Built for Jane Street FTTP program application demonstrating probability, 
combinatorics, and efficient algorithm implementation.
