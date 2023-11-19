from django.test import TestCase
from quizgame.models import *
import re

from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait



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

class ChatTests(ChannelsLiveServerTestCase):
    serve_static = True  # emulate StaticLiveServerTestCase

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            # NOTE: Requires "chromedriver" binary to be installed in $PATH
            cls.driver = webdriver.Chrome()
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self):
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_1")

            self._switch_to_window(0)
            self._post_message("hello")
            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 1 from window 1",
            )
            self._switch_to_window(1)
            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 2 from window 1",
            )
        finally:
            self._close_all_new_windows()

    def test_when_chat_message_posted_then_not_seen_by_anyone_in_different_room(self):
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_2")

            self._switch_to_window(0)
            self._post_message("hello")
            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 1 from window 1",
            )

            self._switch_to_window(1)
            self._post_message("world")
            WebDriverWait(self.driver, 2).until(
                lambda _: "world" in self._chat_log_value,
                "Message was not received by window 2 from window 2",
            )
            self.assertTrue(
                "hello" not in self._chat_log_value,
                "Message was improperly received by window 2 from window 1",
            )
        finally:
            self._close_all_new_windows()

    # === Utility ===

    def _enter_chat_room(self, room_name):
        self.driver.get(self.live_server_url + "/quizgame/room/" + room_name)
        ActionChains(self.driver).send_keys(room_name, Keys.ENTER).perform()
        WebDriverWait(self.driver, 2).until(
            lambda _: room_name in self.driver.current_url
        )

    def _open_new_window(self):
        self.driver.execute_script('window.open("about:blank", "_blank");')
        self._switch_to_window(-1)

    def _close_all_new_windows(self):
        while len(self.driver.window_handles) > 1:
            self._switch_to_window(-1)
            self.driver.execute_script("window.close();")
        if len(self.driver.window_handles) == 1:
            self._switch_to_window(0)

    def _switch_to_window(self, window_index):
        self.driver.switch_to.window(self.driver.window_handles[window_index])

    def _post_message(self, message):
        ActionChains(self.driver).send_keys(message, Keys.ENTER).perform()

    @property
    def _chat_log_value(self):
        return self.driver.find_element(
            by=By.CSS_SELECTOR, value="#chat-log"
        ).get_property("value")
