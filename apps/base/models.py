from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan sana"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Yangilangan sana"))
