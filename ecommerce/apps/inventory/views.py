from django.shortcuts import render

# Create your views here.

def inventory_index(request):
    return render(
        request,
        "inventory/index.html",
        {},
    )

