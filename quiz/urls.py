from django.conf.urls import url
from . import views
from .views import home, profile, QuizListView, QuizListViewPte, QuizListViewOther, CategoriesListView,\
    ViewQuizListByCategory, QuizUserProgressView, QuizMarkingList,\
    QuizMarkingDetail, QuizDetailView, QuizTake, GraphView


urlpatterns = (url(r'^$', views.home, name='home'),
                       url(r'profile/$', 
                       views.profile, 
                       name='profile' ),

                       url(r'change_password/$', 
                       views.change_password, 
                       name='change_password' ),  

                       url(regex=r'^list/$',
                           view=QuizListView.as_view(),
                           name='quiz_index'),

                       url(regex=r'^list_pte/$',
                           view=QuizListViewPte.as_view(),
                           name='quiz_index_pte'),

                       url(regex=r'^list_other/$',
                           view=QuizListViewOther.as_view(),
                           name='quiz_index_other'),

                       url(regex=r'^graphs/(?P<cat_name>(.*))/$',
                           view=GraphView.as_view(),
                           name='quiz_graph'),

                       url(regex=r'^category/$',
                           view=CategoriesListView.as_view(),
                           name='quiz_category_list_all'),

                       url(regex=r'^category/(?P<category_name>[\w|\W-]+)/$',
                           view=ViewQuizListByCategory.as_view(),
                           name='quiz_category_list_matching'),

                       url(regex=r'^progress/$',
                           view=QuizUserProgressView.as_view(),
                           name='quiz_progress'),

                       url(regex=r'^marking/$',
                           view=QuizMarkingList.as_view(),
                           name='quiz_marking'),

                       url(regex=r'^marking/(?P<pk>[\d.]+)/$',
                           view=QuizMarkingDetail.as_view(),
                           name='quiz_marking_detail'),

                       #  passes variable 'quiz_name' to quiz_take view
                       url(regex=r'^(?P<slug>[\w-]+)/$',
                           view=QuizDetailView.as_view(),
                           name='quiz_start_page'),

                       url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
                           view=QuizTake.as_view(),
                           name='quiz_question'),
)