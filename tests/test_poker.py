#!/usr/bin/env python3
"""
Comprehensive Tests for Poker Hand Evaluator.

Tests all hand rankings and equity calculations.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker.card import Card, Rank, Suit, parse_cards
from poker.deck import Deck
from poker.evaluator import HandEvaluator, HandRank, get_hand_strength
from poker.equity import EquityCalculator


class TestCard(unittest.TestCase):
    """Test card representation."""
    
    def test_create_card_from_string(self):
        card = Card("As")
        self.assertEqual(card.rank, Rank.ACE)
        self.assertEqual(card.suit, Suit.SPADES)
    
    def test_create_card_from_rank_suit(self):
        card = Card(rank=Rank.KING, suit=Suit.HEARTS)
        self.assertEqual(str(card), "Kh")
    
    def test_card_equality(self):
        c1 = Card("As")
        c2 = Card("As")
        c3 = Card("Ah")
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
    
    def test_card_comparison(self):
        ace = Card("As")
        king = Card("Ks")
        self.assertTrue(ace > king)
    
    def test_parse_cards(self):
        cards = parse_cards("As Kh Qd")
        self.assertEqual(len(cards), 3)
        self.assertEqual(cards[0].rank, Rank.ACE)
    
    def test_rank_bitmask(self):
        ace = Card("As")
        two = Card("2h")
        self.assertEqual(ace.rank_bit, 1 << 12)
        self.assertEqual(two.rank_bit, 1 << 0)
    
    def test_suit_bitmask(self):
        spade = Card("As")
        heart = Card("Ah")
        club = Card("Ac")
        diamond = Card("Ad")
        self.assertEqual(spade.suit_mask, 0b1000)
        self.assertEqual(heart.suit_mask, 0b0100)
        self.assertEqual(diamond.suit_mask, 0b0010)
        self.assertEqual(club.suit_mask, 0b0001)


class TestDeck(unittest.TestCase):
    """Test deck operations."""
    
    def test_full_deck(self):
        deck = Deck()
        self.assertEqual(len(deck), 52)
    
    def test_draw_cards(self):
        deck = Deck()
        hand = deck.draw(5)
        self.assertEqual(len(hand), 5)
        self.assertEqual(len(deck), 47)
    
    def test_deck_exclude(self):
        excluded = parse_cards("As Ks")
        deck = Deck(exclude=excluded)
        self.assertEqual(len(deck), 50)
    
    def test_shuffle_reproducible(self):
        import random
        deck1 = Deck()
        deck2 = Deck()
        deck1.shuffle(random.Random(42))
        deck2.shuffle(random.Random(42))
        self.assertEqual(deck1.draw(5), deck2.draw(5))


class TestHandEvaluator(unittest.TestCase):
    """Test hand evaluation for all rankings."""
    
    def test_royal_flush(self):
        cards = parse_cards("As Ks Qs Js Ts")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.ROYAL_FLUSH)
    
    def test_straight_flush(self):
        cards = parse_cards("9h 8h 7h 6h 5h")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.STRAIGHT_FLUSH)
    
    def test_four_of_a_kind(self):
        cards = parse_cards("As Ah Ad Ac Ks")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.FOUR_OF_A_KIND)
    
    def test_full_house(self):
        cards = parse_cards("As Ah Ad Ks Kh")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.FULL_HOUSE)
    
    def test_flush(self):
        cards = parse_cards("As Ks Qs Js 2s")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.FLUSH)
    
    def test_straight(self):
        cards = parse_cards("9s 8h 7d 6c 5s")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.STRAIGHT)
    
    def test_straight_ace_low(self):
        """Test wheel (A2345) straight."""
        cards = parse_cards("As 2h 3d 4c 5s")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.STRAIGHT)
    
    def test_straight_ace_high(self):
        """Test broadway (AKQJT) straight."""
        cards = parse_cards("As Kh Qd Jc Ts")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.STRAIGHT)
    
    def test_three_of_a_kind(self):
        cards = parse_cards("As Ah Ad Ks Qh")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.THREE_OF_A_KIND)
    
    def test_two_pair(self):
        cards = parse_cards("As Ah Ks Kh Qd")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.TWO_PAIR)
    
    def test_one_pair(self):
        cards = parse_cards("As Ah Ks Qh Jd")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.ONE_PAIR)
    
    def test_high_card(self):
        cards = parse_cards("As Kh Qd Jc 9s")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.HIGH_CARD)
    
    def test_hand_comparison_different_ranks(self):
        """Royal flush beats straight flush."""
        royal = parse_cards("As Ks Qs Js Ts")
        straight_flush = parse_cards("9h 8h 7h 6h 5h")
        
        royal_result = HandEvaluator.evaluate(royal)
        sf_result = HandEvaluator.evaluate(straight_flush)
        
        self.assertTrue(royal_result > sf_result)
    
    def test_hand_comparison_same_rank_kicker(self):
        """Higher kicker wins."""
        pair_aces_k = parse_cards("As Ah Ks Qh Jd")
        pair_aces_q = parse_cards("As Ah Qs Jh Td")
        
        result1 = HandEvaluator.evaluate(pair_aces_k)
        result2 = HandEvaluator.evaluate(pair_aces_q)
        
        self.assertTrue(result1 > result2)
    
    def test_7_card_evaluation(self):
        """Test 7-card hand finds best 5."""
        cards = parse_cards("As Ah Ad Ac Ks Kh 2c")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.FOUR_OF_A_KIND)
    
    def test_full_house_vs_flush(self):
        """Full house beats flush."""
        full_house = parse_cards("As Ah Ad Ks Kh")
        flush = parse_cards("As Ks Qs Js 9s")
        
        fh_result = HandEvaluator.evaluate(full_house)
        f_result = HandEvaluator.evaluate(flush)
        
        self.assertTrue(fh_result > f_result)
    
    def test_two_pair_ordering(self):
        """Higher two pair wins."""
        aces_kings = parse_cards("As Ah Ks Kh 2d")
        kings_queens = parse_cards("Ks Kh Qs Qh Ad")
        
        result1 = HandEvaluator.evaluate(aces_kings)
        result2 = HandEvaluator.evaluate(kings_queens)
        
        self.assertTrue(result1 > result2)


class TestEquityCalculator(unittest.TestCase):
    """Test Monte Carlo equity calculations."""
    
    def test_aces_vs_kings_preflop(self):
        """AA should beat KK ~80% of the time."""
        aces = parse_cards("As Ah")
        kings = parse_cards("Ks Kh")
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            aces, kings, num_simulations=5000, seed=42
        )
        
        # AA vs KK is approximately 80-20
        self.assertGreater(eq1.equity, 0.75)
        self.assertLess(eq1.equity, 0.90)
    
    def test_coinflip_matchup(self):
        """Pair vs two overcards is ~50-50."""
        pair = parse_cards("7s 7h")
        overcards = parse_cards("As Kh")
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            pair, overcards, num_simulations=5000, seed=42
        )
        
        # Should be roughly 50-50
        self.assertGreater(eq1.equity, 0.40)
        self.assertLess(eq1.equity, 0.60)
    
    def test_dominated_hand(self):
        """Dominated hand should lose most of the time."""
        ak = parse_cards("As Kh")
        aq = parse_cards("Ah Qd")  # Dominated by AK
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            ak, aq, num_simulations=5000, seed=42
        )
        
        # AK dominates AQ (~73%)
        self.assertGreater(eq1.equity, 0.65)
    
    def test_flush_draw_equity(self):
        """Flush draw on flop has ~35% equity."""
        hero = parse_cards("As 2s")  # Two spades
        board = parse_cards("Ks 7s 2h")  # Two spades on board
        
        result = EquityCalculator.calculate_equity(
            hero, board, num_simulations=5000, seed=42
        )
        
        # With 9 outs twice, flush draw should have decent equity
        self.assertGreater(result.equity, 0.30)
    
    def test_set_vs_overpair(self):
        """Set should beat overpair ~90%+."""
        set_hand = parse_cards("7s 7h")
        overpair = parse_cards("As Ah")
        board = parse_cards("7d 2c 3h")  # 7 on board gives set
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            set_hand, overpair, board, num_simulations=3000, seed=42
        )
        
        # Set vs overpair is ~90%
        self.assertGreater(eq1.equity, 0.85)
    
    def test_equity_sums_to_one(self):
        """Equities should sum to approximately 1."""
        hand1 = parse_cards("As Kh")
        hand2 = parse_cards("Qd Qc")
        
        eq1, eq2 = EquityCalculator.calculate_matchup(
            hand1, hand2, num_simulations=1000, seed=42
        )
        
        total = eq1.equity + eq2.equity
        self.assertAlmostEqual(total, 1.0, places=2)
    
    def test_preflop_equity_vs_random(self):
        """Premium hands should have high equity vs random."""
        aces = parse_cards("As Ah")
        
        result = EquityCalculator.preflop_equity(
            aces, num_simulations=3000, seed=42
        )
        
        # AA vs random is ~85%
        self.assertGreater(result.equity, 0.80)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""
    
    def test_same_hand_is_tie(self):
        """Identical hands should tie."""
        hand1 = parse_cards("As Kh Qd Jc 9s")
        hand2 = parse_cards("Ac Kd Qs Jh 9c")
        
        result1 = HandEvaluator.evaluate(hand1)
        result2 = HandEvaluator.evaluate(hand2)
        
        self.assertEqual(result1.strength, result2.strength)
    
    def test_wheel_straight_vs_six_high(self):
        """Six-high straight beats wheel."""
        wheel = parse_cards("5s 4h 3d 2c As")  # A-5 straight
        six_high = parse_cards("6s 5h 4d 3c 2h")  # 2-6 straight
        
        wheel_result = HandEvaluator.evaluate(wheel)
        six_result = HandEvaluator.evaluate(six_high)
        
        self.assertTrue(six_result > wheel_result)
    
    def test_steel_wheel(self):
        """A2345 of same suit is straight flush."""
        cards = parse_cards("5s 4s 3s 2s As")
        result = HandEvaluator.evaluate(cards)
        self.assertEqual(result.rank, HandRank.STRAIGHT_FLUSH)
    
    def test_quads_kicker(self):
        """Higher kicker wins with quads."""
        quads_ace = parse_cards("7s 7h 7d 7c As")
        quads_king = parse_cards("7s 7h 7d 7c Ks")
        
        result1 = HandEvaluator.evaluate(quads_ace)
        result2 = HandEvaluator.evaluate(quads_king)
        
        self.assertTrue(result1 > result2)


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("   POKER HAND EVALUATOR - TEST SUITE")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCard))
    suite.addTests(loader.loadTestsFromTestCase(TestDeck))
    suite.addTests(loader.loadTestsFromTestCase(TestHandEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestEquityCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("   ✅ ALL TESTS PASSED!")
    else:
        print("   ❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
