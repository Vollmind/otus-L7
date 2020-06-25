from django.contrib import admin
from .models import Question, UserReq, Answer, Tag, UserRate

# Register your models here.

admin.site.register(Question)
admin.site.register(UserReq)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(UserRate)