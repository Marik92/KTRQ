from django.contrib import admin
import quiz
from quiz.models import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class QuizAdminForm(forms.ModelForm):
    """
    below is from
    http://stackoverflow.com/questions/11657682/
    django-admin-interface-using-horizontal-filter-with-
    inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=("Вопросы"),
        widget=FilteredSelectMultiple(
            verbose_name=("Вопросы"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial =\
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', )
    search_fields = ('description',)

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category', )


class SubCategoryAdmin(admin.ModelAdmin):
    search_fields = ('sub_category', )
    list_display = ('sub_category', 'category',)
    list_filter = ('category',)

class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    fields = ['question', 'category', 'sub_category',
              'figure', 'answer_order', 'explanation']
    inlines = [AnswerInline]
    search_fields = ['category',]

class PositionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ['name']

class FilialAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(correctValue)
admin.site.register(Answer)
admin.site.register(Position, PositionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Filial, FilialAdmin)