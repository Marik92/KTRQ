from django import forms
from django.forms.widgets import RadioSelect, Textarea
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choice_list = [x for x in question.get_answers_list()]
        self.fields["answers"] = forms.MultipleChoiceField(choices=choice_list,
                                                   widget=forms.CheckboxSelectMultiple)


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)

class ProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('city',)