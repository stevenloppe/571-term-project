from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

TEMPLATE_DIRS = (
    'os.path.join(BASE_DIR, "templates"),'
)

def index(request):
    return render(request,"index.html")

#class IndexView(generic.DetailView):
#    template_name = 'webApp/index.html'
