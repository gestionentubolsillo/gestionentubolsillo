from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.template import loader

# Create your views here.
@require_GET
def home(request):
    template = loader.get_template('home/home.html')
    return HttpResponse(template.render({}, request))
