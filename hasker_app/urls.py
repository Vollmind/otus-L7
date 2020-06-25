from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.QuestionRateOrderedListView.as_view(), name='question_list'),
    path('last', views.QuestionDateOrderedListView.as_view(), name='question_list_date_ordered'),
    path('question/search', views.QuestionSearchListView.as_view(), name='question_search'),
    path('question/<int:pk>/', views.QuestionView.as_view(), name='question_detail'),
    path('<str:obj_type>/<int:obj_id>/vote_down', views.vote_down, name='vote_down'),
    path('<str:obj_type>/<int:obj_id>/vote_up', views.vote_up, name='vote_up'),
    path('question/<int:question_id>/answer', views.post_answer, name='post_answer'),
    path('question/ask', views.ask_question, name='ask_question'),

    path(
        'account/logout',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'
    ),
    path(
        'account/login',
        auth_views.LoginView.as_view(template_name='hasker_app/login.html'),
        name='login'
    ),
    path(
        'account/register',
        views.create_user,
        name='register'
    ),
    path(
        'account/edit/',
        views.edit_user,
        name='edit_account'
    )
]