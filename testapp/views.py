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
from django.conf import settings


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

        all_recordings = []
        if user_data and 'lessons' not in user_data.keys():
            user_data['lessons'] = {}

        if not user_data:
            user_data = {}

        for each_recording in user_data['lessons']:
            data = {
                'id': each_recording,
                'lessonname': user_data['lessons']['name'],
                'path': user_data['lessons'][each_recording]
            }
            try:
                data['name'] = user_data['lessons'][each_recording]['name'] + '.wav'
            except:
                data['name'] = str(each_recording) + '.wav'

            all_recordings.append(data)

        context={
            'lessons': all_unattended_lessons,
            'total_lessions': alllessons.count(),
            'all_recordings': all_recordings
        }


        if len(all_unattended_lessons) == 0:
            context['success'] = True
        else:
            context['lessonid'] = all_unattended_lessons[0].id

        return render(request, self.template_name, context)

    def post(self,request, *args, **kwargs):
        """Method to select record page."""
        data = request.FILES['audio_data']
        lessonid = request.POST['lessonid']
        lesson = Lesson.objects.get(id=lessonid)

        complete_name = os.path.join(settings.MEDIA_ROOT + '/userdata/' + str(request.user.id) + '/' + str(lessonid) + ".wav")
        print(complete_name)

        path = settings.MEDIA_ROOT + '/userdata/'+ str(request.user.id)
        if not os.path.exists(path):
            os.makedirs(path)

        file = open(complete_name, "wb")
        file.write(data.read())
        file.close()

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        update_condition = {
            'userid': request.user.id,
            'username': request.user.username
        }

        user_data = mdb.find_one(collection_name="users", condition=update_condition)

        if user_data:
            try:
                lessons = user_data['lessons']
            except:
                lessons = {}
        else:
            lessons = {}

        lessons[lessonid] = lessonid
        lessons['name'] = str(lesson)

        mdb.update_data(
            collection_name="users",
            update_data={'lessons': lessons},
            update_condition=update_condition,
            upsert=True
        )

        mdb.close_connection()
        return JsonResponse({'status':'success', 'next': 1 })
