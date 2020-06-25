from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserReq(models.Model):
    avatar = models.ImageField(default='../static/hasker_app/default_avatar.jpg')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_req")


class Tag(models.Model):
    name = models.TextField()


class Question(models.Model):
    label = models.TextField(null=True)
    text = models.TextField(null=True)
    user = models.ForeignKey(UserReq, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)


class Answer(models.Model):
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(UserReq, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    confirmed = models.BooleanField(default=False)


class UserRate(models.Model):
    user = models.ForeignKey(UserReq, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="rates", null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="rates", null=True, blank=True)
    rate = models.IntegerField()
