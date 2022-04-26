from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

def main(request):
    return render(request, "main.html")

