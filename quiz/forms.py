from django import forms
from django.forms.widgets import RadioSelect, Textarea
from .models import *
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
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

class ProfileForm(forms.ModelForm):
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    filial = forms.ModelChoiceField(queryset=Filial.objects.all(), empty_label="Пусто", widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Пусто", widget=forms.Select(attrs={'class': 'form-control'}))
    position = forms.ModelChoiceField(queryset=Position.objects.all(), empty_label="Пусто", widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = UserProfile
        fields = ('city', 'filial', 'department', 'position', 'avatar')