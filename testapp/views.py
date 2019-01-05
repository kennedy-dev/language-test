from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import render
from testapp.models import Lesson
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
import os
from language.helpers.db_helper import MongoDBConnect
from django.http import JsonResponse

class RecordSuccessPage(LoginRequiredMixin, TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        """Method to select record page."""
        context = {}

        return render(request, self.template_name, context)

class RecordPage(LoginRequiredMixin, TemplateView):

    template_name = 'pages/record.html'

    def get(self,request, *args, **kwargs):
        """Method to select record page.."""
        alllessons = Lesson.objects.all()

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        condition = {
            'userid': request.user.id,
            'username': request.user.username
        }

        user_data = mdb.find_one(collection_name="users",condition=condition)

        lessons = None
        if user_data:
            try:
                lessons = user_data['lessons']
            except:
                lessons = None

        all_unattended_lessons = []
        if lessons:
            for each_lesson in alllessons:
                if str(each_lesson.id) not in list(lessons.keys()):
                    all_unattended_lessons.append(each_lesson)
        else:
            all_unattended_lessons = list(alllessons)

        if len(all_unattended_lessons) == 0:
            return HttpResponseRedirect('/success/')

        context = {
            'lessons': all_unattended_lessons,
            'lessonid': all_unattended_lessons[0].id,
            'total_lessions': alllessons.count()
        }

        return render(request, self.template_name, context)

    def post(self,request, *args, **kwargs):
        """Method to select record page."""
        data = request.FILES['audio_data']
        lessonid = request.POST['lessonid']
        name_of_file = request.FILES['audio_data'].name
        complete_name = os.path.join('/home/userdata/' + str(request.user.id), name_of_file + ".wav")

        if not os.path.exists('/home/userdata/'+ str(request.user.id)):
            os.makedirs('/home/userdata/'+ str(request.user.id))

        file = open(complete_name, "w")
        file.write(complete_name)
        file.close()

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        update_condition = {
            'userid': request.user.id,
            'username': request.user.username
        }

        user_data = mdb.find_one(collection_name="users", condition=update_condition)

        if user_data and user_data['lessons']:
            lessons = user_data['lessons']
        else:
            lessons = {}

        lessons[lessonid] = data.read()

        mdb.update_data(
            collection_name="users",
            update_data={'lessons': lessons},
            update_condition=update_condition,
            upsert=True
        )

        mdb.close_connection()
        return JsonResponse({'status':'success', 'next': 1 })
