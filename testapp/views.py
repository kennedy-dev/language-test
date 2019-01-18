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


class AnalystPage(LoginRequiredMixin, TemplateView):
    template_name = 'pages/analyst.html'

    def get(self, request, *args, **kwargs):
        """Method to select analyst page."""
        context = {}
        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        condition = {
            'userid': request.user.id,
            'username': request.user.username
        }

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

        all_recordings = mdb.find(collection_name="recording",condition=condition)
        all_recording_ids = [each_recording['lessonid'] for each_recording in all_recordings]
        all_unattended_lessons = []

        if all_recordings:
            for each_lesson in alllessons:
                if str(each_lesson['id']) not in all_recording_ids:
                    all_unattended_lessons.append(each_lesson)
        else:
            all_unattended_lessons = list(alllessons)

        for each_recording in all_recordings:
            data = {
                'id': each_recording['id'],
                'lessonname': each_recording['lessonname'],
                'path': each_recording
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

        user_data = mdb.find_one(collection_name="users", condition=update_condition)

        lessons={}
        lessons['lessonid'] = lessonid
        lessons['lessonname'] = str(lesson)

        mdb.insert_data(
            collection_name="recordings",
            insert_data={
                'lessons': lessons,
                'user_data': user_data.__dict__,
                'recordname': str(lessonid) + ".wav"
            }
        )

        mdb.close_connection()
        return JsonResponse({'status':'success', 'next': 1 })
