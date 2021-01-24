from django.urls import path, re_path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("add/", views.ExtractorCreateView.as_view(), name="extractor-create"),
    path("extract/", views.extract_text, name="extract-keyphrases"),
]
