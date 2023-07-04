from http import HTTPStatus

from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def csrf_failure(request: HttpRequest, reason='') -> HttpResponse:
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(
        request, 'pages/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
