from django.contrib import admin
from wikisearch.models import Extractor


# Register your models here.]
class ExtractorAdmin(admin.ModelAdmin):
    list_display = ["description"]


admin.site.register(Extractor, ExtractorAdmin)
