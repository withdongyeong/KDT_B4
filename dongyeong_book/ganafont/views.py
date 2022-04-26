from django.shortcuts import render
from django.http import HttpResponse

def ganafont(request):
    return render(request, "ganafont.html")