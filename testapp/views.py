from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import render


class TestPage(LoginRequiredMixin, TemplateView):

    template_name = 'pages/testpage.html'

    def get(self,request, *args, **kwargs):
        """Method to select jobs.."""
        context = {}
        return render(request, self.template_name, context)
