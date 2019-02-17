from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from language.users.forms import SignUpForm
from django.views.generic import View, TemplateView
from language.helpers.db_helper import MongoDBConnect
from testapp.models import Lesson


User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserListView(LoginRequiredMixin, ListView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_list_view = UserListView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class UserCreationView(TemplateView):

    def post(self,request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            name = form.cleaned_data.get('name')
            gender = form.cleaned_data.get('gender')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            user.save()
            lessons = Lesson.objects.all()

            insert_data = {
                'name':name,
                'userid':user.id,
                'username':username,
                'email': email,
                'gender': gender
            }

            mdb = MongoDBConnect(db_name='language', username="root", password="root")
            mdb.insert_data(collection_name="users", insert_data=insert_data)

            for each_lesson in lessons:
                book = each_lesson.book.__dict__
                chapter = each_lesson.chapter.__dict__
                verse = each_lesson.verse.__dict__
                lesson = each_lesson.__dict__

                if '_state' in lesson.keys():
                    del lesson['_state']

                if '_state' in book.keys():
                    del book['_state']

                if '_state' in chapter.keys():
                    del chapter['_state']

                if '_state' in verse.keys():
                    del verse['_state']

                update_data = {
                    'lesson': lesson,
                    'book': book,
                    'chapter': chapter,
                    'verse': verse,
                    'user_data': insert_data,
                    'recordname': "",
                    'approved': False,
                    'recordtime': ""
                }

                mdb.insert_data(collection_name="recordings", insert_data=update_data)

            mdb.close_connection()

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'account/signup.html', {'form': form})

    def get(self,request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        form = SignUpForm()
        return render(request, 'account/signup.html', {'form': form})


user_create_view = UserCreationView.as_view()
