from django import forms
from wikisearch.models import Extractor


class ExtractorForm(forms.ModelForm):
    class Meta:
        model = Extractor
        fields = ("description",)
