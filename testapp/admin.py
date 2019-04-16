from django.contrib import admin
from .models import *

admin.site.site_header = "Language Settings Admin"
admin.site.site_title = "Language App Admin Portal"
admin.site.index_title = "Welcome to Language App Portal"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """ Admin class for Sentup Subject Result."""

    list_display = (
        "__str__", "created",
    )

admin.site.register(Book)
admin.site.register(Chapter)
admin.site.register(Verse)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    change_form_template = "admin/lesson_change_form.html"

    class Media:
        js = (
            "//ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js",
            "js/loadbdata.js",
        )

from django.contrib.auth.models import Group
from allauth.account.models import EmailAddress
from django.contrib.sites.models import Site

admin.site.unregister(Group)
# admin.site.unregister(Site)
admin.site.unregister(EmailAddress)
