from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from .models import Size

# Create your views here.
def index(request):
    return HttpResponse("Project 3: TODO")


def sizes(request):
    context = {
        "sizes": Size.objects.all()
    }
    return render(request, "orders/sizes.html", context)
