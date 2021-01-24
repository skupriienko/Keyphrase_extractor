from django.db import models


class Extractor(models.Model):
    description = models.TextField(blank=True, null=True, help_text="Enter the text")

    def __str__(self):
        return self.description
