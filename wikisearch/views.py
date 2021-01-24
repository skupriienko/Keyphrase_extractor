from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .models import Extractor
from .forms import ExtractorForm

import re
import pandas as pd
import urllib.request

from datetime import datetime
from bs4 import BeautifulSoup

import nltk
from nltk.corpus import stopwords


def index(request):

    return render(request, "wikisearch/index.html", context={})


def search(request):
    form = ExtractorForm()

    context = {"form": form}
    return render(request, "wikisearch/search.html", context=context)


class ExtractorCreateView(CreateView):
    model = Extractor
    form_class = ExtractorForm
    success_url = reverse_lazy("index")


nltk.download("stopwords")
nltk.download("wordnet")
stopwords = stopwords.words("english")
wn = nltk.WordNetLemmatizer()

# Extract last text from model Extractor
def extract_text(request):
    my_text = Extractor.objects.last()
    description = my_text.description

    # Clean text from unnecessary symbols
    def clean_with_regex(text):
        clean_endlines = re.sub("\.\n", ".+++", text)
        clean_endlines = re.sub("!\n", "!+++", clean_endlines)
        clean_endlines = re.sub(":\n", "+++", clean_endlines)
        clean_endlines = re.sub("\n", " ", clean_endlines)
        enter_endlines = re.sub("\+{3}", "\n", clean_endlines)
        return enter_endlines

    corpora_cleaned = clean_with_regex(description)
    corpora_lower = corpora_cleaned.lower()
    # Find most significant words in the cleaned text
    match_words = re.findall(r"\b[A-Za-z']+\b(?=[,\.!\?:;\"—]+)", corpora_lower, re.I)
    # Remove stopwords
    text = [word for word in match_words if word not in stopwords]
    # Remove long and short words
    text_without_longwords = [
        item for item in text if (len(item) < 13) and (len(item) > 2)
    ]

    # Create lemmas from words
    def lemmatizing(tokenized_text):
        text = wn.lemmatize(tokenized_text)
        return text

    text_lemmitized = list(map(lambda x: lemmatizing(x), text_without_longwords))

    # Create a request to retrieve data using urllib.request
    def url_request(url):
        # Define headers
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Accept-Language": "uk-UA, ukr;q=0.5",
        }
        request = urllib.request.Request(url, headers=HEADERS)
        # Set timeout for requests
        response = urllib.request.urlopen(request, timeout=4)
        status_code = response.status

        # if no error, then read the response contents
        if status_code >= 200 and status_code < 300:
            # read the data from the URL
            data = response.read().decode("utf8")
        return data

    # Check if word has disambiguation page in wikipedia
    def get_desambiguation_url(my_soup):
        for a in my_soup.find_all("a", href=True):
            if a["href"] == "/wiki/Category:Disambiguation_pages":
                return True
        return float("NaN")

    wiki_url = "https://en.wikipedia.org/w/index.php?search="

    wikipages = []

    now = datetime.utcnow()
    timestamp = now.strftime("%d.%m.%Y %H:%I")

    for search_word in text_lemmitized[:15]:
        search_url = f"{wiki_url}{search_word}"

        data = url_request(search_url)
        # Create html soup with lxml parser
        soup = BeautifulSoup(data, "lxml")

        wiki = get_desambiguation_url(soup)

        wikipages.append(wiki)

    # Create dataframe with 15 most significant words
    wiki_df = pd.DataFrame(
        list(zip(text_lemmitized[:15], wikipages)), columns=["word", "disambig"]
    )
    # Add timestamp column to dataframe
    wiki_df["timestamp"] = timestamp

    # Pack lists for template context
    mylist = zip(wiki_df["word"], wiki_df["disambig"], wiki_df["timestamp"])

    context = {
        "my_raw_text": description,
        "mylist": mylist,
    }

    return render(request, "wikisearch/extract_keyphrases.html", context=context)
