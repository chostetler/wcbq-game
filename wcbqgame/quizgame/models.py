from django.db import models

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=255)
    answer_text = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='associated_verse')

    def __str__(self):
        if len(self.question_text)>100:
            return f'{self.question_text[0:97]}...'
        else:
            return self.question_text

class BibleVerse(models.Model):
    book = models.CharField(max_length=50)
    chapter = models.PositiveIntegerField()
    verse = models.PositiveIntegerField()
    text = models.TextField()

    def __str__(self):
        return f'{self.book} {self.chapter}:{self.verse}'

class Guess(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='associated_question')
    guess_text = models.CharField(max_length=255)
    guess_date = models.DateTimeField('time guessed')

    def __str__(self):
        return self.guess_text
