#!/usr/bin/env python3
"""
Poker Hand Evaluator & Equity Calculator Demo

Demonstrates:
1. Hand evaluation with all rankings
2. Monte Carlo equity calculation (10,000 simulations)
3. Matchup analysis between known hands

Run with: python demo.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker import Card, HandEvaluator, HandRank, EquityCalculator
from poker.card import parse_cards, cards_to_str


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def demonstrate_hand_rankings():
    """Show all poker hand rankings."""
    print_header("POKER HAND RANKINGS DEMONSTRATION")
    
    hands = [
        ("Royal Flush", "As Ks Qs Js Ts"),
        ("Straight Flush", "9h 8h 7h 6h 5h"),
        ("Four of a Kind", "As Ah Ad Ac Ks"),
        ("Full House", "As Ah Ad Ks Kh"),
        ("Flush", "As Ks Qs Js 2s"),
        ("Straight", "9s 8h 7d 6c 5s"),
        ("Straight (Wheel)", "5s 4h 3d 2c As"),
        ("Three of a Kind", "As Ah Ad Ks Qh"),
        ("Two Pair", "As Ah Ks Kh Qd"),
        ("One Pair", "As Ah Ks Qh Jd"),
        ("High Card", "As Kh Qd Jc 9s"),
    ]
    
    print("\n🃏 Evaluating all hand rankings:\n")
    print(f"{'Hand Type':<20} {'Cards':<25} {'Result':<20}")
    print("-" * 65)
    
    for name, cards_str in hands:
        cards = parse_cards(cards_str)
        result = HandEvaluator.evaluate(cards)
        pretty = cards_to_str(cards, pretty=True)
        print(f"{name:<20} {pretty:<25} {result.description:<20}")


def demonstrate_hand_comparison():
    """Show hand comparison logic."""
    print_header("HAND COMPARISON DEMONSTRATION")
    
    comparisons = [
        ("Full House vs Flush", "As Ah Ad Ks Kh", "Ks Qs Js 9s 7s"),
        ("Higher Pair Wins", "As Ah Ks Qh Jd", "Ks Kh As Qh Jd"),
        ("Kicker Decides", "As Ah Ks Qh Jd", "As Ah Ks Qh Td"),
        ("Same Hand = Tie", "As Kh Qd Jc 9s", "Ac Kd Qs Jh 9c"),
    ]
    
    print("\n⚖️ Comparing hands:\n")
    
    for scenario, hand1_str, hand2_str in comparisons:
        hand1 = parse_cards(hand1_str)
        hand2 = parse_cards(hand2_str)
        
        result1 = HandEvaluator.evaluate(hand1)
        result2 = HandEvaluator.evaluate(hand2)
        
        comparison = HandEvaluator.compare_hands(hand1, hand2)
        if comparison > 0:
            winner = "Hand 1 wins"
        elif comparison < 0:
            winner = "Hand 2 wins"
        else:
            winner = "Tie"
        
        print(f"📊 {scenario}")
        print(f"   Hand 1: {cards_to_str(hand1, pretty=True):<25} → {result1.description}")
        print(f"   Hand 2: {cards_to_str(hand2, pretty=True):<25} → {result2.description}")
        print(f"   Result: {winner}")
        print()


def demonstrate_equity_calculator():
    """Show Monte Carlo equity calculation."""
    print_header("MONTE CARLO EQUITY CALCULATOR")
    
    print("\n🎲 Monte Carlo Method: Simulate 10,000 random outcomes")
    print("   to estimate win probability (equity).\n")
    
    # Example scenario from the prompt
    print("📝 Scenario: You hold A♠ K♠")
    print("   Board shows: 2♥ 7♣ J♠ (flop)")
    print("   Question: What's your equity vs a random hand?\n")
    
    hero = parse_cards("As Ks")
    board = parse_cards("2h 7c Js")
    
    print("   Running 10,000 simulations...")
    
    result = EquityCalculator.calculate_equity(
        hero_cards=hero,
        board_cards=board,
        num_simulations=10000,
        seed=42
    )
    
    print(f"\n   ✅ Results:")
    print(f"      Wins:   {result.wins:>5} ({result.win_pct:.1f}%)")
    print(f"      Ties:   {result.ties:>5} ({result.tie_pct:.1f}%)")
    print(f"      Losses: {result.losses:>5} ({result.lose_pct:.1f}%)")
    print(f"      ────────────────────")
    print(f"      Equity: {result.equity*100:.2f}%")
    print(f"      Time:   {result.time_ms:.1f}ms")


def demonstrate_matchup_analysis():
    """Show head-to-head matchup analysis."""
    print_header("HEAD-TO-HEAD MATCHUP ANALYSIS")
    
    matchups = [
        ("AA vs KK (Classic Cooler)", "As Ah", "Ks Kh"),
        ("Pair vs Overcards (Coinflip)", "7s 7h", "As Kh"),
        ("AK vs AQ (Domination)", "As Kh", "Ah Qd"),
        ("Suited Connectors vs High Card", "7s 6s", "Ah Td"),
    ]
    
    print("\n🆚 Preflop Matchup Analysis (10,000 simulations each):\n")
    
    for name, hand1_str, hand2_str in matchups:
        hand1 = parse_cards(hand1_str)
        hand2 = parse_cards(hand2_str)
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            hand1, hand2, num_simulations=10000, seed=42
        )
        
        h1_pretty = cards_to_str(hand1, pretty=True)
        h2_pretty = cards_to_str(hand2, pretty=True)
        
        print(f"📊 {name}")
        print(f"   {h1_pretty:<10} vs {h2_pretty:<10}")
        print(f"   {eq1.equity*100:>5.1f}%      {eq2.equity*100:>5.1f}%")
        print()


def demonstrate_board_runout():
    """Show equity changing through streets."""
    print_header("EQUITY THROUGH STREETS")
    
    hero = parse_cards("As Ks")  # Ace-King suited
    villain = parse_cards("Qh Qd")  # Pocket Queens
    
    h_pretty = cards_to_str(hero, pretty=True)
    v_pretty = cards_to_str(villain, pretty=True)
    
    print(f"\n🃏 {h_pretty} vs {v_pretty}")
    print(f"   (AK suited vs Pocket Queens)\n")
    
    # Preflop
    eq1, eq2 = EquityCalculator.calculate_matchup(
        hero, villain, board=[], num_simulations=5000, seed=42
    )
    print(f"   Preflop:        AKs: {eq1.equity*100:>5.1f}%  |  QQ: {eq2.equity*100:>5.1f}%")
    
    # Flop
    flop = parse_cards("Js 9s 3c")
    eq1, eq2 = EquityCalculator.calculate_matchup(
        hero, villain, board=flop, num_simulations=5000, seed=42
    )
    print(f"   Flop (J♠ 9♠ 3♣):  AKs: {eq1.equity*100:>5.1f}%  |  QQ: {eq2.equity*100:>5.1f}%")
    print(f"                   (AKs has flush draw + overcards)")
    
    # Turn (brick)
    turn = flop + parse_cards("2h")
    eq1, eq2 = EquityCalculator.calculate_matchup(
        hero, villain, board=turn, num_simulations=5000, seed=42
    )
    print(f"   Turn (+ 2♥):     AKs: {eq1.equity*100:>5.1f}%  |  QQ: {eq2.equity*100:>5.1f}%")
    
    # River (hits flush!)
    river = turn + parse_cards("7s")
    eq1, eq2 = EquityCalculator.calculate_matchup(
        hero, villain, board=river, num_simulations=5000, seed=42
    )
    print(f"   River (+ 7♠):    AKs: {eq1.equity*100:>5.1f}%  |  QQ: {eq2.equity*100:>5.1f}%")
    print(f"                   (AKs made the flush!)")


def performance_benchmark():
    """Benchmark evaluation speed."""
    print_header("PERFORMANCE BENCHMARK")
    
    from poker.deck import Deck
    import random
    
    print("\n⚡ Testing evaluation speed:\n")
    
    # Single hand evaluation
    cards = parse_cards("As Kh Qd Jc Ts 9s 8h")
    
    start = time.time()
    iterations = 10000
    for _ in range(iterations):
        HandEvaluator.evaluate(cards)
    elapsed = time.time() - start
    
    per_eval = (elapsed / iterations) * 1000000  # microseconds
    print(f"   7-card evaluation: {per_eval:.2f} μs per hand")
    print(f"   Throughput: {iterations/elapsed:,.0f} hands/second")
    
    # Equity calculation
    hero = parse_cards("As Kh")
    board = parse_cards("2s 7c Jd")
    
    start = time.time()
    EquityCalculator.calculate_equity(hero, board, num_simulations=10000)
    elapsed = time.time() - start
    
    print(f"\n   10,000 equity simulations: {elapsed*1000:.1f} ms")
    print(f"   Simulations/second: {10000/elapsed:,.0f}")


def run_interactive_evaluator():
    """Interactive hand input."""
    print_header("INTERACTIVE HAND EVALUATOR")
    
    print("\n📝 Enter 5 cards to evaluate (e.g., 'As Kh Qd Jc Ts')")
    print("   Or type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("   Enter cards: ").strip()
            if user_input.lower() in ('quit', 'q', 'exit'):
                break
            
            cards = parse_cards(user_input)
            if len(cards) < 5:
                print("   ⚠️ Please enter at least 5 cards.\n")
                continue
            
            result = HandEvaluator.evaluate(cards)
            print(f"   → {result.description}")
            print(f"   → Cards: {cards_to_str(result.cards, pretty=True)}\n")
            
        except ValueError as e:
            print(f"   ⚠️ Error: {e}\n")
        except KeyboardInterrupt:
            break


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("   POKER HAND EVALUATOR & EQUITY CALCULATOR")
    print("   Jane Street FTTP Application Project")
    print("=" * 60)
    
    # Run demos
    demonstrate_hand_rankings()
    demonstrate_hand_comparison()
    demonstrate_equity_calculator()
    demonstrate_matchup_analysis()
    demonstrate_board_runout()
    performance_benchmark()
    
    print_header("DEMO COMPLETE")
    
    print("\n🎯 Key Takeaways:")
    print("   1. Bitmasking for O(1) flush/straight detection")
    print("   2. Monte Carlo simulation for equity calculation")
    print("   3. 10,000+ simulations for statistical significance")
    print("   4. Applications to trading: incomplete information, EV, risk")
    
    print("\n📚 Run tests with: python tests/test_poker.py")
    print("   Interactive mode: python demo.py --interactive")
    
    # Check for interactive flag
    if len(sys.argv) > 1 and sys.argv[1] in ('--interactive', '-i'):
        run_interactive_evaluator()


if __name__ == "__main__":
    main()
