# Create your models here.

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Language(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=200, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    # Meta and Strings:
    class Meta:
        """ Meta data for Language model"""
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return self.title


class Lesson(models.Model):
    language = models.ForeignKey('Language', on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=200, null=True, blank=True)
    text_to_read = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    # Meta and Strings:
    class Meta:
        """ Meta data for Lesson model"""
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")

    def __str__(self):
        return str(self.language.title) + ": " + self.title
