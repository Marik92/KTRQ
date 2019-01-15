from django import forms
import json
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

    dpositions = {}
    list_positions = []
    for position in Position.objects.all():
        if position.department.name in dpositions:
            dpositions[position.department.name].append(position.name)
        else:
            dpositions[position.department.name] = [position.name]
        list_positions.append((position.name,position.name))

    departments = [str(department) for department in Department.objects.all()]

    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    filial = forms.ModelChoiceField(queryset=Filial.objects.all(), empty_label="Пусто", widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.ChoiceField(choices=([(department, department) for department in departments]), widget=forms.Select(attrs={'class': 'form-control'}))
    position = forms.ChoiceField(choices=(list_positions), widget=forms.Select(attrs={'class': 'form-control'}))
    avatar = forms.ImageField()

    departments = json.dumps(departments)
    positions = json.dumps(dpositions)

    class Meta:
        model = UserProfile
        fields = ('city', 'filial', 'department', 'position', 'avatar',)