from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import render
from testapp.models import Lesson, Language
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
import os
from language.helpers.db_helper import MongoDBConnect
from django.http import JsonResponse
from django.conf import settings
import time
from bson.objectid import ObjectId


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

        all_records = list(
            mdb.find("recordings")
        )
        records = []
        for each_record in all_records:
            each_record['recordid'] = str(each_record['_id'])
            records.append(each_record)

        languages = Language.objects.all()

        mdb.close_connection()

        context['records'] = records
        context['user'] = request.user
        context['has_permission'] = True
        from django.contrib import admin
        context['site_header'] = admin.site.site_header
        context['site_title'] = admin.site.site_title
        context['index_title'] = admin.site.index_title

        context['languages'] = languages
        context['site_url'] = '/'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Method to select analyst page."""

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        print(request.POST)
        if 'select' in request.POST.get('id', ''):
            record_id = request.POST.get('id', '').replace('select_','')
            language_id = request.POST.get('value', '')

            language = Language.objects.get(id=language_id).__dict__
            del language['_state']

            mdb.update_data(
                collection_name="recordings",
                update_condition={'_id': ObjectId(record_id)},
                update_data={"approvedlanguage":language}
            )

            mdb.close_connection()
            return JsonResponse({"status": "success"})

        elif 'input_' in request.POST.get('id', ''):
            record_id = request.POST.get('id', '').replace('input_','')
            approved = request.POST.get('value', '')
            if approved == 'true':
                approved = True
            else:
                approved = False

            mdb.update_data(
                collection_name="recordings",
                update_condition={'_id': ObjectId(record_id)},
                update_data={"approved": approved}
            )

            mdb.close_connection()
            return JsonResponse({"status": "success"})

        mdb.close_connection()
        return JsonResponse({"status": "fail"})


class RecordPage(LoginRequiredMixin, TemplateView):

    template_name = 'pages/record.html'

    def get(self,request, *args, **kwargs):
        """Method to select record page.."""
        alllessons = Lesson.objects.all()

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        condition = {
            'user_data.userid': request.user.id,
            'user_data.username': request.user.username
        }

        user_recording = []
        all_recordings = mdb.find(collection_name="recordings",condition=condition)
        all_recording_ids = []

        for each_recording in all_recordings:
            data = {
                'id': str(each_recording['_id']),
                'lessonname': each_recording['lessons']['lessonname'],
                'path': '/userdata/' + str(request.user.id) + '/'
            }
            all_recording_ids.append(each_recording['lessons']['lessonid'])

            data['name'] = each_recording['recordname']
            user_recording.append(data)

        all_unattended_lessons = []

        if all_recordings:
            for each_lesson in alllessons:
                if str(each_lesson.id) not in all_recording_ids:
                    all_unattended_lessons.append(each_lesson)
        else:
            all_unattended_lessons = list(alllessons)

        context={
            'lessons': all_unattended_lessons,
            'total_lessions': alllessons.count(),
            'all_recordings': user_recording
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

        path = settings.MEDIA_ROOT + '/userdata/'+ str(request.user.id)
        if not os.path.exists(path):
            os.makedirs(path)

        file = open(complete_name, "wb")
        file.write(data.read())
        file.close()

        mdb = MongoDBConnect(db_name='language', username="root", password="root")
        condition = {
            'userid':request.user.id
        }
        user_data = mdb.find_one(collection_name="users", condition=condition)

        lessons={}
        lessons['lessonid'] = lessonid
        lessons['lessonname'] = str(lesson)

        mdb.update_data(
            collection_name="recordings",
            update_data={
                'lessons': lessons,
                'user_data': user_data,
                'recordname': str(lessonid) + ".wav",
                'approved':False,
                'recordtime': time.time()
            },
            update_condition={
                'lessons': lessons,
                'user_data': user_data,
                'recordname': str(lessonid) + ".wav"
            },
            upsert=True
        )

        mdb.close_connection()
        return JsonResponse({'status':'success', 'next': 1 })
