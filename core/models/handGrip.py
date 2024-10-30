from django.db import models
from uploader.models import Image


class Handgrip(models.Model):
    graph = models.ForeignKey(
        Image,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "Registros de Força de Preensão Manual"
