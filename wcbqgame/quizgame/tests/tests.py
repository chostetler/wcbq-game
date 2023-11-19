from django.test import TestCase
from quizgame.models import *
import re

class QuizGameTests(TestCase):
    def setUp(self):
        self.version = BibleVersion.objects.create(name='ESV')
        self.verse = BibleVerse.objects.create(
            book="John", chapter=3, verse=16, text="For God so loved the world that he gave his one and only son, that whoever believes in him shall not perish but have eternal life", version = self.version)
        self.question = Question.objects.create(
            question_text="Who gave his one and only son?"
            )
        self.answer = Answer.objects.create(question=self.question, text="God")

    # Test creation
    def test_version_creation(self):
        version = BibleVersion.objects.get(name="ESV")
        self.assertEqual(version.name, "ESV")

    def test_verse_creation(self):
        verse = BibleVerse.objects.get(book="John")
        self.assertEqual(verse.chapter, 3)
        self.assertEqual(verse.verse, 16)
        self.assertEqual(verse.text, "For God so loved the world that he gave his one and only son, that whoever believes in him shall not perish but have eternal life")
        self.assertEqual(verse.version, self.version)

    def test_answer_creation(self):
        answer = Answer.objects.get(text="God")
        self.assertEqual(answer.question, self.question)

    def test_player_creation(self):
        player = Player.objects.create(username="steve", color_hex="#FFAA00")
        self.assertEqual(player.username, "steve")
        self.assertEqual(player.color_hex, "#FFAA00")

    def test_question_guess_string_correct_method(self):
        correct_answer = Answer.objects.create(question=self.question, text="God")
        self.assertTrue(self.question.guess_string_correct("God"))
        self.assertFalse(self.question.guess_string_correct("Jesus"))

    def test_answer_matches_guess_string_method(self):
        # Assuming you have implemented the matches_guess_string method in the Answer model
        correct_answer = Answer.objects.create(question=self.question, text="Correct answer")
        incorrect_answer = Answer.objects.create(question=self.question, text="Incorrect answer")
        
        self.assertTrue(correct_answer.matches_guess_string("Correct-answer"))
        self.assertFalse(correct_answer.matches_guess_string("Incorrect guess"))
