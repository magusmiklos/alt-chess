from django.shortcuts import render
from django.http import JsonResponse

def hello_word(request):
    return JsonResponse({"message": "hello word!"})
