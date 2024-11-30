import unittest
from unittest.mock import MagicMock
from hypothesis import given, assume
from hypothesis import strategies as st

from nmm.players import Player, PlayerState, AIPlayer, CMDPlayer


class MockedPlayer(Player):
    def play(self, *args, **kwargs):
        return None


class MockedAIPlayer(AIPlayer):
    def play(self, *args, **kwargs):
        return None


class TestPlayer(unittest.TestCase):

    @given(st.text(min_size=1))
    def test_player_initialization(self, name:str):
        player = MockedPlayer(name)

    @given(st.text(min_size=1))
    def test_player_name_1(self, name:str):
        player = MockedPlayer(name)
        self.assertEqual(player.name, name)

    @given(st.text(min_size=1))
    def test_player_name_2(self, name:str):
        player = MockedPlayer(name)
        self.assertEqual(player._name, name)

    @given(st.text(min_size=1))
    def test_player_equality_1(self, name:str):
        player1 = MockedPlayer(name)
        player2 = MockedPlayer(name)
        self.assertEqual(player1, player2)

    @given(st.text(min_size=1), st.text(min_size=1))
    def test_player_inequality_1(self, name1:str, name2:str):
        assume(name1 != name2)
        player1 = MockedPlayer(name1)
        player2 = MockedPlayer(name2)
        self.assertNotEqual(player1, player2)

    @given(st.text(min_size=1))
    def test_player_equality_3(self, name:str):
        player = MockedPlayer(name)
        self.assertEqual(player, name)

    @given(st.text(min_size=1), st.text(min_size=1))
    def test_player_inequality_4(self, name1:str, name2:str):
        assume(name1 != name2)
        player = MockedPlayer(name1)
        self.assertNotEqual(player, name2)

    @given(st.text(min_size=1), st.text(min_size=1))
    def test_player_name_immutability(self, name:str, new_name:str):
        player = MockedPlayer(name)
        with self.assertRaises(AttributeError):
            player.name = new_name

    @given(st.text(min_size=1), st.text(min_size=1) )
    def test_player_name_immutability_2(self, name:str, new_name:str):
        player = MockedPlayer(name)
        with self.assertRaises(AttributeError):
            player._name = new_name

    @given(st.text(min_size=1))
    def test_player_str_repr(self, name:str):
        player = MockedPlayer(name)
        self.assertEqual(str(player), name)
        self.assertEqual(repr(player), name)

    @given(st.text(min_size=1))
    def test_player_clone(self, name:str):
        player = MockedPlayer(name)
        self.assertEqual(player.clone(), player)

    def test_abstract_class(self):
        with self.assertRaises(TypeError):
            Player("Player 1")

    def test_call_calls_play(self):
        obj = MockedPlayer("test")
        obj.play = MagicMock(return_value=None)
        self.assertFalse(obj.play.called)
        obj(None, None)
        self.assertTrue(obj.play.called)

    def test_hash(self):
        obj1 = MockedPlayer("test")
        obj2 = MockedPlayer("test")
        self.assertEqual(hash(obj1), hash(obj2))

    def test_hash_inequality(self):
        obj1 = MockedPlayer("test1")
        obj2 = MockedPlayer("test2")
        self.assertNotEqual(hash(obj1), hash(obj2))

class TestAIPlayer(unittest.TestCase):
    @given(st.text(min_size=1))
    def test_abstract_class(self, name:str):
        player = MockedAIPlayer(name)
        self.assertEqual(player.name, name)
        self.assertIsInstance(player, AIPlayer)

