import random
from math import sqrt,pi,exp,pow
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.contrib.auth.forms import UserCreationForm, User, PasswordChangeForm
from django.views.generic.edit import FormView
from .forms import QuestionForm, SignUpForm, ProfileForm, UserForm
from .models import Quiz, Category, Progress, Sitting, Question, UserProfile
from django.contrib.auth import login, authenticate, update_session_auth_hash

def home(request):
    """Функция рендерит html-страницу и передает ей объекты из модели"""

    return render(request, 'home.html')

def Register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            #handle_uploaded_file(request.FILES['avatar'])
            user_form.save()
            profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            return redirect('profile')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    success_exams = []
    failed_exams = []
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.userprofile)
    progress, c = Progress.objects.get_or_create(user=request.user)
    all_exams = Sitting.objects.filter(user=request.user)
    for i in all_exams:
        if i.get_percent_correct >= i.quiz.pass_mark:
            success_exams.append(i)
        else:
            failed_exams.append(i)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'exams': progress.show_exams(),
        'success_exams': success_exams,
        'failed_exams': failed_exams
    })

def handle_uploaded_file(f):
    with open('quiz/media/profile_images/' + str(f), 'wb+') as destination:
        print ('YES')
        for chunk in f.chunks():
            destination.write(chunk)


def profile_get(request, user_id):
    try:
        user_form = User.objects.get(id=user_id)
        print (user_form)
    except ObjectDoesNotExist:
        print ('GGWP')

    return render(request, 'profile_get.html', {'user_form': user_form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

def rating_list(request):
    """Функция рендерит html-страницу и передает ей объекты из модели"""

    return render(request, 'rating_list.html')

def rating_category_list(request):
    """Функция рендерит html-страницу и передает ей объекты из модели"""
    cat_list = Category.objects.all()
    return render(request, 'rating_category_list.html', {'cat_list': cat_list})

def rating_tests_list(request):
    """Функция рендерит html-страницу и передает ей объекты из модели"""
    quiz_list = Quiz.objects.filter(draft=False)
    return render(request, 'rating_tests_list.html', {'quiz_list': quiz_list})

def standard_normal_distribution(x):
	return (1./sqrt(2*pi))*exp(-0.5*pow(x,2))

def snd(x):
	return standard_normal_distribution(x)

def ci_lower_bound(positive, total, power=0.001):
    '''Функцию для подсчета рейтинга на основе алгоритма 
    Эдвина Уилсона. Принимает в качестве аргументов: 
    1) Число успешных тестов, которые сдал пользователь
    2) Общее число тестов, которые прошел пользователь
    3) Уровень надежности, дефолтный = 0.001, для расчета квантиля'''
    if not total:
        return 0
    z = snd((1-power)/2)
    n = total
    phat = 1.0*positive/n
    return (phat + z*z/(2*n) - z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)

class LuckyRatingView(TemplateView):
    template_name = 'rating_ten_lucky.html'

    def get_context_data(self, **kwargs):
        context = super(LuckyRatingView, self).get_context_data(**kwargs)
        users = User.objects.all()
        user_result = {}
        top_ten = {}
        
        for user in users:
            progress, c = Progress.objects.get_or_create(user=user)
            tests = progress.show_exams()
            if len(tests) == 0:
                pass
            else:
                count = 0
                for objects in tests:
                    if objects.get_percent_correct >= objects.quiz.pass_mark:
                        count = count + 1
                    else:
                        pass
                user_result[user] = [len(tests), count]
        
        for key, value in user_result.items():
            rating = ci_lower_bound(value[1],value[0])
            top_ten[key] = rating
    
        result = dict(sorted(top_ten.items(), key=lambda x: x[1], reverse=True))
        context = {'form': result.items()}
        return context

class LooserRatingView(TemplateView):
    template_name = 'rating_ten_looser.html'

    def get_context_data(self, **kwargs):
        context = super(LooserRatingView, self).get_context_data(**kwargs)
        users = User.objects.all()
        user_result = {}
        top_ten = {}
        
        for user in users:
            progress, c = Progress.objects.get_or_create(user=user)
            tests = progress.show_exams()
            if len(tests) == 0:
                pass
            else:
                count = 0
                for objects in tests:
                    if objects.get_percent_correct >= objects.quiz.pass_mark:
                        count = count + 1
                    else:
                        pass
                user_result[user] = [len(tests), count]
        
        for key, value in user_result.items():
            rating = ci_lower_bound(value[1],value[0])
            revert_rating = 1 - rating
            top_ten[key] = revert_rating
    
        result = dict(sorted(top_ten.items(), key=lambda x: x[1], reverse=True))
        context = {'form': result.items()}
        return context

class QuizRatingDetailView(TemplateView):
    template_name = 'rating_quiz_detail.html'
    
    def get_context_data(self, quiz_id, **kwargs):
        context = super(QuizRatingDetailView, self).get_context_data(**kwargs)
        users = User.objects.all()
        user_result = {}
        top_ten = {}

        for user in users:
            tests = Sitting.objects.filter(complete=True, quiz__id=quiz_id, user=user)

            if len(tests) == 0:
                pass
            else:
                count = 0
                for objects in tests:
                    if objects.get_percent_correct >= objects.quiz.pass_mark:
                        count = count + 1
                    else:
                        pass
                user_result[user] = [len(tests), count]

        context['exams'] = tests
        
        for key, value in user_result.items():
            rating = ci_lower_bound(value[1],value[0])
            top_ten[key] = rating
    
        result = dict(sorted(top_ten.items(), key=lambda x: x[1], reverse=True))
        context = {'form': result.items()}
        return context


class CategoryRatingDetailView(TemplateView):
    template_name = 'rating_quiz_detail.html'
    
    def get_context_data(self, cat_id, **kwargs):
        context = super(CategoryRatingDetailView, self).get_context_data(**kwargs)
        users = User.objects.all()

        for user in users:
            progress, c = Progress.objects.get_or_create(user=user)
            context[user] = progress.list_all_cat_scores
            print (progress)

        return context


class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list.html'

    def get_queryset(self):
        queryset = super(QuizListView, self).get_queryset()
        return queryset.filter(draft=False)

class QuizListViewPte(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list_pte.html'

    def get_queryset(self):
        queryset = super(QuizListViewPte, self).get_queryset()
        return queryset.filter(draft=False)

class QuizListViewOther(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list_other.html'

    def get_queryset(self):
        queryset = super(QuizListViewOther, self).get_queryset()
        return queryset.filter(draft=False)

class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CategoriesListView(ListView):
    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)


class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        return context


class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        '''Функция возвращает список выполненных тестов
        позволяет и позволяет производить поиск в таблице по имени
        или фамилии пользователя в темплэйте sitting_list'''
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(Q(user__first_name__icontains=user_filter) | Q(user__last_name__icontains=user_filter))

        return queryset


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] =\
            context['sitting'].get_questions(with_answers=True)
        return context


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(request.user,
                                                        self.quiz)
        else:
            self.sitting = self.anon_load_sitting()

        if self.sitting is False:
            return render(request, 'single_complete.html')

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):

        if form_class is None:
            form_class = QuestionForm

        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()
        else:
            self.question = self.anon_next_question()
            self.progress = self.anon_sitting_progress()

        #if self.question.__class__ is Essay_Question:
            #form_class = EssayForm

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
        else:
            self.form_valid_anon(form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return self.final_result_anon()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess_list = form.cleaned_data['answers']

        is_correct = self.question.check_if_correct(guess_list)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess_list,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess_list)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] =\
                self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] =\
                self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False:
            self.sitting.delete()

        return render(self.request, 'result.html', results)

    def anon_load_sitting(self):
        if self.quiz.single_attempt is True:
            return False
        
        if self.quiz.attempt_choise == 'D':
            return False

        if self.quiz.anon_q_list() in self.request.session:
            return self.request.session[self.quiz.anon_q_list()]
        else:
            return self.new_anon_quiz_session()

    def new_anon_quiz_session(self):
        """
        Sets the session variables when starting a quiz for the first time
        as a non signed-in user
        """
        self.request.session.set_expiry(259200)  # expires after 3 days
        questions = self.quiz.get_questions()
        question_list = [question.id for question in questions]

        if self.quiz.random_order is True:
            random.shuffle(question_list)

        if self.quiz.max_questions and (self.quiz.max_questions
                                        < len(question_list)):
            question_list = question_list[:self.quiz.max_questions]

        # session score for anon users
        self.request.session[self.quiz.anon_score_id()] = 0

        # session list of questions
        self.request.session[self.quiz.anon_q_list()] = question_list

        # session list of question order and incorrect questions
        self.request.session[self.quiz.anon_q_data()] = dict(
            incorrect_questions=[],
            order=question_list,
        )

        return self.request.session[self.quiz.anon_q_list()]

    def anon_next_question(self):
        next_question_id = self.request.session[self.quiz.anon_q_list()][0]
        return Question.objects.get_subclass(id=next_question_id)

    def anon_sitting_progress(self):
        total = len(self.request.session[self.quiz.anon_q_data()]['order'])
        answered = total - len(self.request.session[self.quiz.anon_q_list()])
        return (answered, total)

    def form_valid_anon(self, form):
        guess_list = form.cleaned_data['answers']
        print (guess_list)
        is_correct = self.question.check_if_correct(guess_list)

        if is_correct:
            self.request.session[self.quiz.anon_score_id()] += 1
            anon_session_score(self.request.session, 1, 1)
        else:
            anon_session_score(self.request.session, 0, 1)
            self.request\
                .session[self.quiz.anon_q_data()]['incorrect_questions']\
                .append(self.question.id)

        self.previous = {}
        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess_list,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}

        self.request.session[self.quiz.anon_q_list()] =\
            self.request.session[self.quiz.anon_q_list()][1:]

    def final_result_anon(self):
        score = self.request.session[self.quiz.anon_score_id()]
        q_order = self.request.session[self.quiz.anon_q_data()]['order']
        max_score = len(q_order)
        percent = int(round((float(score) / max_score) * 100))
        session, session_possible = anon_session_score(self.request.session)
        if score is 0:
            score = "0"

        results = {
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'session': session,
            'possible': session_possible
        }

        del self.request.session[self.quiz.anon_q_list()]

        if self.quiz.answers_at_end:
            results['questions'] = sorted(
                self.quiz.question_set.filter(id__in=q_order)
                                      .select_subclasses(),
                key=lambda q: q_order.index(q.id))

            results['incorrect_questions'] = (
                self.request
                    .session[self.quiz.anon_q_data()]['incorrect_questions'])

        else:
            results['previous'] = self.previous

        del self.request.session[self.quiz.anon_q_data()]

        return render(self.request, 'result.html', results)


def anon_session_score(session, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score.
    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score
                                    without modification
    Left this as an individual function for unit testing
    """
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]


class GraphView(TemplateView):
    template_name = 'graphs.html'

    def get_context_data(self, cat_name, **kwargs):
        context = super(GraphView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        exams_for_graph = Sitting.objects.filter(user=self.request.user, complete=True, quiz__category__category=cat_name)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        context['category'] = exams_for_graph[0].quiz.category
        return context
