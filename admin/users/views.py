import json

from django.http import HttpResponse


def check_superuser_auth(request):
    if not request.user.is_authenticated:
        return HttpResponse("User is not authenticated", status=401)

    response_data = dict()
    if request.user.is_superuser:
        response_data.update(is_superuser=True)
    else:
        response_data.update(is_superuser=False)

    return HttpResponse(json.dumps(response_data), status=200)
