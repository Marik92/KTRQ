import re
import json
from urllib import request
from django.utils.timezone import now
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect
from model_utils.managers import InheritanceManager
from django.core.validators import RegexValidator, validate_comma_separated_integer_list
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Filial(models.Model):
    name = models.CharField(
        verbose_name=("Филиал"),
        max_length=200,
        unique = True,
        null = True,
        blank = True,
    )

    class Meta:
        verbose_name = ("Филиал")
        verbose_name_plural = ("Филиалы")

    def __str__(self):
        return self.name

class Department(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE,
        verbose_name=("Филиал"))
    name = models.CharField(
        verbose_name=("Департамент/Служба/Отдел"),
        max_length=200,
        null = True, 
        blank = True,)

    class Meta:
        verbose_name = ("Департамент/Служба/Отдел")
        verbose_name_plural = ("Департамент/Служба/Отдел")

    def __str__(self):
        return self.name

class Position(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE,
        verbose_name=("Филиал"), default = 1, related_name='filial_article_set')
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
        verbose_name=("Департамент/Служба/Отдел"), default = 1, related_name='department_article_set')
    name = models.CharField(
        verbose_name=("Должность"),
        max_length=200,
        unique = True,
        null = True,
        blank = True,)

    class Meta:
        verbose_name = ("Должность")
        verbose_name_plural = ("Должности")

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User,
        on_delete=models.CASCADE)

    city = models.CharField(
        verbose_name=("Город/Село"),
        max_length=100,
        unique=True,
        null = True,
        blank = True,
    )

    filial = models.ForeignKey(
        Filial, 
        on_delete=models.CASCADE,
        verbose_name=("Филиал"),
        null=True
    )

    department = models.ForeignKey(Department, on_delete=models.CASCADE,
        verbose_name=("Департамент/Служба/Отдел"), null=True,
    )

    position = models.ForeignKey(Position, on_delete=models.CASCADE,
        verbose_name=("Должность"),
        null=True,
    )

    def __str__(self):
        return "%s's profile" % self.user

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0]) 

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category)
                                   .lower())

        new_category.save()
        return new_category


class Category(models.Model):

    category = models.CharField(
        verbose_name=("Категория теста"),
        max_length=250, blank=True,
        unique=True, null=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = ("Категория")
        verbose_name_plural = ("Категории")

    def __str__(self):
        return self.category


class SubCategory(models.Model):

    sub_category = models.CharField(
        verbose_name=("Подкатегория"),
        max_length=250, blank=True, null=True)

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=("Категория"))

    objects = CategoryManager()

    class Meta:
        verbose_name = ("Подкатегория")
        verbose_name_plural = ("Подкатегории")

    def __str__(self):
        return self.sub_category + " (" + self.category.category + ")"



class Quiz(models.Model):

    title = models.CharField(
        verbose_name=("Название теста"),
        max_length=60, blank=False, help_text=("Введите название теста"))

    description = models.TextField(
        verbose_name=("Описание теста"),
        blank=True, help_text=("Введите описание теста"))

    url = models.SlugField(
        max_length=60, blank=False,
        help_text=("Читаемая url-ссылка для пользователя"),
        verbose_name=("user friendly url"))

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=("Категория"))

    random_order = models.BooleanField(
        blank=False, default=True,
        verbose_name=("Случайная последовательность выдачи вопросов"),
        help_text=("Если да, показывает вопросы в случайной последовательности"))

    max_questions = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=("Максимальное кол-во вопросов"),
        help_text=("Максимальное количество вопросов за одну попытку сдачи теста"))

    answers_at_end = models.BooleanField(
        blank=False, default=False,
        help_text=("Если да, после ответа пользователя на вопрос, будет показан правильный вариант"),
        verbose_name=("Правильный ответ в конце"))

    exam_paper = models.BooleanField(
        blank=False, default=False,
        help_text=("Если да, то результат каждой попытки"
                    " будет сохраняться. Необходимо для маркировки."),
        verbose_name=("Результат теста"))

    single_attempt = models.BooleanField(
        blank=False, default=False,
        help_text=("Если да, то будет разрешена только одна попытка сдачи теста."
                    " Незарегиситрированные пользователи не смогут сдать экзамен."),
        verbose_name=("Одна попытка?"))

    pass_mark = models.SmallIntegerField(
        blank=True, default=0,
        verbose_name=("Порог прохождения теста"),
        help_text=("Процент необходимый для сдачи теста"),
        validators=[MaxValueValidator(100)])

    success_text = models.TextField(
        blank=True, help_text=("Показывает введенный текст если пользователь сдал тест."),
        verbose_name=("Объявление в случае сдачи теста"))

    fail_text = models.TextField(
        verbose_name=("Объявление в случае провала теста"),
        blank=True, help_text=("Показывает введенный текст если пользователь провалил тест."))

    draft = models.BooleanField(
        blank=True, default=False,
        verbose_name=("В процессе разработки"),
        help_text=("Если да, то тест будет виден только админам."))

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.url = re.sub('\s+', '-', self.url).lower()

        self.url = ''.join(letter for letter in self.url if
                           letter.isalnum() or letter == '-')

        if self.single_attempt is True:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = ("Тест")
        verbose_name_plural = ("Тесты")

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def anon_score_id(self):
        return str(self.id) + "_score"

    def anon_q_list(self):
        return str(self.id) + "_q_list"

    def anon_q_data(self):
        return str(self.id) + "_data"





class ProgressManager(models.Manager):

    def new_progress(self, user):
        new_progress = self.create(user=user,
                                   score="")
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Данный класс используется для записи результата пользователя в разных тестах
    и категориях. Данные сохраняются в csv-формате:
        категория, результат, возможный результат, 
        категория, результат, возможный результат... итд ...
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=("Пользователь"))

    score = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024, verbose_name=("Результат"))

    objects = ProgressManager()

    class Meta:
        verbose_name = ("Прогресс пользователя")
        verbose_name_plural = ("Записи прогресса пользователя")

    @property
    def list_all_cat_scores(self):
        """
        Возвращает словарь, где ключом является категория и айтемом список
        из 3-ех чисел.
        Первое число это количество правильных ответов
        Второе число это максимально возможный результат
        Третее число это процент правильных ответов
        Словарь имеет один ключи для каждой категории, которую вы создадите

        """
        score_before = self.score
        output = {}

        for cat in Category.objects.all():
            to_find = re.escape(cat.category) + r",(\d+),(\d+),"
            #  Regex-группа 1 это результат, Regex-группа 2 это максимально возможный результат

            match = re.search(to_find, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))

                try:
                    percent = int(round((float(score) / float(possible))
                                        * 100))
                except:
                    percent = 0

                output[cat.category] = [score, possible, percent]

            else:  # если категория еще не добавлена, добавить ее.
                self.score += cat.category + ",0,0,"
                output[cat.category] = [0, 0]

        if len(self.score) > len(score_before):
            # Если новая категория добавлена, сохранить изменения.
            self.save()

        return output

    def update_score(self, question, score_to_add=0, possible_to_add=0):
        """
        Pass in question object, amount to increase score
        and max possible.
        Does not return anything.
        """
        category_test = Category.objects.filter(category=question.category)\
                                        .exists()

        if any([item is False for item in [category_test,
                                           score_to_add,
                                           possible_to_add,
                                           isinstance(score_to_add, int),
                                           isinstance(possible_to_add, int)]]):
            return ("Ошибка"), ("категория не существует или неккоректный результат")

        to_find = re.escape(str(question.category)) +\
            r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) +\
                abs(possible_to_add)

            new_score = ",".join(
                [
                    str(question.category),
                    str(updated_score),
                    str(updated_possible), ""
                ])

            # заменить старый результат новым
            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            #  if not present but existing, add with the points passed in
            self.score += ",".join(
                [
                    str(question.category),
                    str(score_to_add),
                    str(possible_to_add),
                    ""
                ])
            self.save()

    def show_exams(self):
        """
        Находит предыдущие записи сдачи тестов промаркированных как 'exam papers'
        и возвращает список успешных тестов.
        """
        return Sitting.objects.filter(user=self.user, complete=True)



class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.question_set.all() \
                                            .select_subclasses() \
                                            .order_by('?')
        else:
            question_set = quiz.question_set.all() \
                                            .select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Список вопросов пуст. '
                                       'Пожалуйста создайте список вопросов.')

        if quiz.max_questions and quiz.max_questions < len(question_set):
            question_set = question_set[:quiz.max_questions]

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True and self.filter(user=user,
                                                       quiz=quiz,
                                                       complete=True)\
                                               .exists():
            return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        return sitting


class Sitting(models.Model):
    """
    Данный класс используется для сохранения прогресса тестируемого.
    Подменяет сессию, используемую анонимными пользователями
    Question_order это список PKs или IDs всех вопросов в данном тесте
    Question_list это список чисел, которые показывают IDs всех неотвеченных
    пользователем вопросов в csv-формате.
    Incorrect_questions это список IDs всех вопросов на которые пользователь
    ответил неправильно в csv-формате.
    Sitting удаляется когда тест заканчивается, если quiz.exam_paper == True
    User_answers это объект в формате JSON в котором сохранятся все PKs или IDs вопросов 
    на которые пользователь дал ответ.

    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=("Пользователь"))

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name=("Тест"))

    question_order = models.CharField(validators=[validate_comma_separated_integer_list],
        max_length=1024, verbose_name=("Список PKs вопросов в данном тесте"))

    question_list = models.CharField(validators=[validate_comma_separated_integer_list],
        max_length=1024, verbose_name=("Список PKs неотвеченных вопросов"))

    incorrect_questions = models.CharField(validators=[validate_comma_separated_integer_list],
        max_length=1024, blank=True, verbose_name=("Список PKs вопросов с неправильным ответом"))

    current_score = models.IntegerField(verbose_name=("Текущий результат"))

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name=("Завершен"))

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name=("Ответы пользователя"))

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name=("Начало теста"))

    end = models.DateTimeField(null=True, blank=True, verbose_name=("Конец теста"))

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", ("Can see completed exams.")),)

    def get_first_question(self):
        """
        Возвращает следующий вопрос
        Если не найдено вопросов, возвращает False
        Не УДАЛЯЕТ вопрос из списка

        """
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())
        if divisor < 1:
            return 0            # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds uid of incorrect question to the list.
        The question object must be passed in.
        """
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        """
        Returns a list of non empty integers, representing the pk of
        questions
        """
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.quiz.success_text
        else:
            return self.quiz.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.quiz.question_set.filter(id__in=question_ids)
                                  .select_subclasses(),
            key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        """
        Returns the number of questions answered so far and the total number of
        questions.
        """
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total


class correctValue (models.Model):
    value = models.CharField(max_length=5, verbose_name='Правильность ответа')

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = 'Правильность ответа'
        verbose_name_plural = 'Правильность ответов'


ANSWER_ORDER_OPTIONS = (
    ('content', ('Контент')),
    ('random', ('Случайно')),
    ('none', ('None')))


class Question (models.Model):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS, default='random',
        help_text=("Правило по которому будут"
                    " показаны ответы пользователю:"
                    " случайно, по контенту или none"),
        verbose_name=("Правило вывода ответов"))

    quiz = models.ManyToManyField(Quiz,
                                  verbose_name=("Тест"),
                                  blank=True)

    category = models.ForeignKey(Category,
                                 verbose_name=("Категория"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE)

    sub_category = models.ForeignKey(SubCategory,
                                     verbose_name=("Подкатегория"),
                                     blank=True,
                                     null=True,
                                     on_delete=models.CASCADE)

    figure = models.ImageField(upload_to='uploads/%Y/%m/%d',
                               blank=True,
                               null=True,
                               verbose_name=("Рисунок к вопросу"))

    question = models.CharField(max_length=200, unique=True, verbose_name='Вопрос')

    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text=("Объяснение будет показано "
                                               "после ответа на вопрос."),
                                   verbose_name=('Объяснение'))

    def check_if_correct(self, guess_list):
        "Функция проверят ответы на правильность. В качестве аргумента принимает guess_list со списком ID ответов, которые дал пользователь"
        
        #Вытаскиваем ID-шники всех ответов в данном вопросе и заносим их в список
        all_answer = Answer.objects.filter(question__question=self.question)
        all_answers_ids = []
        for answer in all_answer:
            all_answers_ids.append(answer.id)
        print (all_answers_ids)

        #Вытаскиваем ID-шники только правильных ответов и заносим в список
        correct_answers_ids = []
        for ids in all_answers_ids:
            value = Answer.objects.get(id=ids)
            if str(value.correct_or_not) == "Да":
                correct_answers_ids.append(ids)
            else:
                pass
        print (correct_answers_ids)

        #Вытаскиваем ID-шники ответов пользователя и если они 
        user_answers_ids = []
        for guess in guess_list:
            user_answers_ids.append(int(guess))
        print (user_answers_ids)
        
        #Сравниваем список с правильными ответам и список с ответами пользователя с помощью кортежей
        #если списки одинаковые то выдаст такое же кол-во элементов что и в списке с правильными ответами
        #поэтому просто сравниваем длинну списков
        result = list(set(user_answers_ids) & set(correct_answers_ids))
        if len(correct_answers_ids) == len(result):
            return True
        else:
            return False
    
    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.answer) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).answer

    
    objects = InheritanceManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question   


class Answer (models.Model):
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    answer = models.CharField(max_length=1024, verbose_name='Ответ')
    
    correct_or_not = models.ForeignKey(correctValue, 
                                        default='Нет', 
                                        on_delete=models.CASCADE)

    def __str__(self):
        return self.answer
    
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
