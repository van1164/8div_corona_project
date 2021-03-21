from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name = 'login'), # ver1.0
    path('home', views.home, name = 'home'), # ver1.0
    path('poll', views.poll, name = 'poll'), # ver1.0
    path('finish', views.finish, name ='finish'),
    path('officer_result', views.officer_check, name = 'officer_check'),
    path('battalion', views.batta_check, name = 'batta_check'),
    path('brigade', views.brig_check, name = 'brig_check'),
    path('division', views.div_check, name = 'div_check'),
    path('submit', views.submit, name = "submit"),
    path('edit_survey', views.edit_survey, name = "edit_survey")
]