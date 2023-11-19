from django.db import models
import re

# Create your models here.

# Represents a specific bible version
class BibleVersion(models.Model):
    name = models.CharField(max_length=50)

# Class represents a bible verse
class BibleVerse(models.Model):
    book = models.CharField(max_length=50)
    chapter = models.PositiveIntegerField()
    verse = models.PositiveIntegerField()
    text = models.TextField()
    version = models.ForeignKey(BibleVersion, on_delete=models.CASCADE, related_name='verses', blank=True, null=True)

    def __str__(self):
        return f'{self.book} {self.chapter}:{self.verse}'

# Represents a single question
class Question(models.Model):
    question_text = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='questions', blank=True, null=True)

    def __str__(self):
        if len(self.question_text)>100:
            return f'{self.question_text[0:97]}...'
        else:
            return self.question_text
    def guess_string_correct(self, guess:str):
        for answer in self.answers.all():
            if answer.matches_guess_string(guess):
                return True
        return False

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    # Returns true if >2/3 of keywords are found in the guess string
    def matches_guess_string(self, guess: str):
        keywords = set(re.findall(r'\b\w+\b', self.text.upper()))
        guesswords = set(re.findall(r'\b\w+\b', guess.upper()))
        matches = keywords.intersection(guesswords)
        if len(keywords)*0.66 <= len(matches):
            return len(guesswords) <= len(keywords) * 3
        return False

    def __str__(self):
        return self.text



# Classes for game functionality
# Represents one person guessing on a question

class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7)

class Guess(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='associated_question')
    guess_text = models.CharField(max_length=255)
    guess_date = models.DateTimeField('time guessed')
    

    def __str__(self):
        return self.guess_text
