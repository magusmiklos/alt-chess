from .views import hello_word
from django.urls import path

urlpatterns = [
    path('/hello', hello_word)
    
]
