from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from game.constants.messages import ErrorMessages

def custom_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    This function handles the 404 error.It returns a custom 404 page.
    :param request: HttpRequest
    :param exception: Exception
    :return: HttpResponse
    """
    return render(request, '404.html', {'message': ErrorMessages.PAGE_404}, status=404)
