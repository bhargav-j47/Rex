from django.urls import path,include
from .views import Submit,Check

urlpatterns = [

    path('submit/',Submit.as_view()),
    path('check/',Check.as_view()),
    
]
