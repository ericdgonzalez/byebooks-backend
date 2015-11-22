from django.http import HttpResponse
from django.shortcuts import render_to_response

def home(request):
  return HttpResponse('Home Page')

def launchpad(request):
  context = {}
  return render_to_response('launch.html', context)
