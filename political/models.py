from django.db import models

# models.py
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=500)

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=500)

    def __str__(self):
        return self.answer_text
