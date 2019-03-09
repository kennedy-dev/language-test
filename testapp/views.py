from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import render
from testapp.models import Lesson, Language, Book, Chapter, Verse
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
import os
from language.helpers.db_helper import MongoDBConnect
from django.http import JsonResponse
from django.conf import settings
import time
from bson.objectid import ObjectId
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.views import View
from bson.objectid import ObjectId
User = get_user_model()
from django.forms.models import model_to_dict


class RecordSuccessPage(LoginRequiredMixin, TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        """Method to select record page."""
        context = {}
        return render(request, self.template_name, context)


class WordsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/wordcount.html'

    def get(self, request, *args, **kwargs):
        """Method to select record page."""
        context = {
            'lessons': Lesson.objects.all()
        }
        return render(request, self.template_name, context)


class StatisticsPage(LoginRequiredMixin, TemplateView):
    template_name = 'pages/stats.html'

    def get(self, request, *args, **kwargs):
        """Method to select statistics page."""

        context = {}
        user = request.GET.get('user', '')
        book = request.GET.get('book', '')
        chapter = request.GET.get('chapter', '')

        condition = {}

        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        context['users'] = User.objects.all()
        context['books'] = Book.objects.all()
        context['chapters'] = Chapter.objects.all()

        if user:
            condition['user_data.username'] = user
            context['selecteduser'] = user

        if book:
            condition['book.id'] = int(book)
            context['selectedbook'] = int(book)

        if chapter:
            condition['chapter.id'] = int(chapter)
            context['selectedchapter'] = int(chapter)

        all_records = list(
            mdb.find("recordings", condition=condition)
        )

        records = []
        for each_record in all_records:
            each_record['recordid'] = str(each_record['_id'])
            records.append(each_record)

        context['records'] = all_records
        mdb.close_connection()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Method to select statistics page."""
        return JsonResponse({"status": "fail"})


class AnalystPage(LoginRequiredMixin, TemplateView):
    template_name = 'pages/analyst.html'

    def get(self, request, *args, **kwargs):
        """Method to select analyst page."""

        if not request.user.is_superuser:
            return HttpResponseRedirect('/')

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
        if request.user.is_superuser:
            return HttpResponseRedirect('/admin/')
        action = request.GET.get('action', None)
        mdb = MongoDBConnect(db_name='language', username="root", password="root")

        selected_language = request.GET.get('language', None)
        if selected_language:
            selected_language = int(selected_language)

        selected_verse = request.GET.get('verse', None)
        if selected_verse:
            selected_verse = int(selected_verse)

        selected_chapter = request.GET.get('chapter', None)
        if selected_chapter:
            selected_chapter = int(selected_chapter)

        selected_book = request.GET.get('book', None)
        if selected_book:
            selected_book = int(selected_book)

        context = {}

        if str(action) == "delete":
            delete_record_id = request.GET.get('id', None)
            mdb.delete_data(collection_name="recordings", condition={'_id': ObjectId(delete_record_id)})

        if selected_language and selected_verse and selected_chapter and selected_book:
            alllessons = Lesson.objects.filter(
                book__id=selected_book,
                chapter__id=selected_chapter,
                verse__id=selected_verse,
                language_id=selected_language
            )
            if alllessons:
                all_recordings = [alllessons[0]]
            else:
                context['message'] = 'No lesson found for recording.'
        else:
            alllessons = Lesson.objects.all()

        condition = {
            'user_data.userid': request.user.id,
            'user_data.username': request.user.username,
            "recordname": {"$ne":""}
        }

        user_recording = []
        all_recordings = mdb.find(collection_name="recordings",condition=condition)
        all_recording_ids = []

        for each_recording in all_recordings:
            each_recording['path'] = '/userdata/' + str(request.user.id) + '/'
            each_recording['name'] = each_recording['recordname']
            each_recording['record_id'] = str(each_recording['_id'])
            all_recording_ids.append(str(each_recording['lesson']['id']))
            user_recording.append(each_recording)

        all_unattended_lessons = []
        if all_recordings:
            for each_lesson in alllessons:
                if str(each_lesson.id) not in all_recording_ids:
                    all_unattended_lessons.append(each_lesson)
        else:
            all_unattended_lessons = list(alllessons)

        if len(all_unattended_lessons) == 0:
            context['message'] = 'Sorry! No lessons found for recording.'

        context['lessons'] = all_unattended_lessons
        context['total_lessons'] = alllessons.count()
        context['all_recordings'] = user_recording
        context['books'] = Book.objects.all()
        context['languages'] = Language.objects.all()
        context['chapters'] = Chapter.objects.all()
        context['verses'] = Verse.objects.all()
        context['alllessons'] = Lesson.objects.all()

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

        book = lesson.book.__dict__
        chapter = lesson.chapter.__dict__
        verse = lesson.verse.__dict__
        lesson = lesson.__dict__

        del user_data['_id']
        del lesson['_state']

        if '_state' in lesson.keys():
            del lesson['_state']

        if '_state' in book.keys():
            del book['_state']

        if '_state' in chapter.keys():
            del chapter['_state']

        if '_state' in verse.keys():
            del verse['_state']

        mdb.update_data(
            collection_name="recordings",
            update_data={
                'recordname': str(lessonid) + ".wav",
                'approved':False,
                'recordtime': time.time(),
                'lesson': lesson,
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'user_data': user_data,
            },
            update_condition={
                'lesson.id': lesson['id'],
                'user_data.userid': user_data['userid']
            },
            upsert=True
        )

        mdb.close_connection()
        return JsonResponse({'status':'success', 'next': 1 })



class DataView(View):

    def post(self,request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        book_id = request.POST.get('book_id', None)
        chapter_id = request.POST.get('chapter_id', None)
        return_data = {
            'chapters': [],
            'verses': []
        }

        print("Book Id:: ",book_id, "Chapter ID::", chapter_id)
        if book_id:
            chapters = list(Chapter.objects.filter(book__id=book_id))
            verses = list(Verse.objects.filter(chapter__book__id=book_id))

            json_chapters = []
            for each_chapter in chapters:
                json_chapters.append(model_to_dict(each_chapter))

            json_verses = []
            for each_verse in verses:
                json_verses.append(model_to_dict(each_verse))

            return_data['chapters'] = json_chapters
            return_data['verses'] = json_verses

        if chapter_id:
            verses = list(Verse.objects.filter(chapter__id=chapter_id))

            json_verses = []
            for each_verse in verses:
                json_verses.append(model_to_dict(each_verse))

            return_data['verses'] = json_verses

        print(return_data)
        return JsonResponse(return_data)
