from .models import Category


def categories(request):
    # return {"categories": Category.objects.filter(parent=None)}
    return {"categories": Category.objects.all()}
