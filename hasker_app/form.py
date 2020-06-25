from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ImageField, Form, EmailField, widgets, ModelMultipleChoiceField
from django.forms.widgets import Input

from hasker_app.models import Answer, Question, Tag


class MultipleChoiceTagWithAddField(ModelMultipleChoiceField):
    widget = Input(attrs={'placeholder': 'tag1, tag2, tag3'})

    def clean(self, value):
        if value is None or value == '':
            value_list = []
        else:
            value_list = str.split(value, ',')
        if len(value_list) > 3:
            raise ValidationError('Maximum 3 tags!')
        tags = Tag.objects.filter(name__in=value_list).all()
        real_value = [x.id for x in tags]
        for newtag in value_list:
            if all(x.name != newtag for x in tags):
                tag = Tag(name=newtag)
                tag.save()
                real_value.append(tag.id)
        self.queryset = Tag.objects.all()
        return super().clean(real_value)


class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ['text']


class UserForm(UserCreationForm):
    avatar = ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name")
        field_classes = {'username': UsernameField}


class UserEditForm(Form):
    email = EmailField(required=False)
    avatar = ImageField(required=False, widget=widgets.FileInput)


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ('label', 'text', 'tags')
        widgets = {
            'label': Input()
        }
        labels = {
            'label': 'Question'
        }
        field_classes = {
            'tags': MultipleChoiceTagWithAddField
        }
