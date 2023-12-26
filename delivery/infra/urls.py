from django.urls import path

from utils.rolepolicy import URLs

import importlib
from importlib import import_module

app_name = "infra"

urlpatterns = [
]

allUrlKeys = URLs.ALL_URLS.keys()
views = __import__('infra.views')

for url in allUrlKeys:
    urlObj = URLs.ALL_URLS[url]
    p = import_module(urlObj["base"])
    f = getattr(p, urlObj["name"])
    p = path(urlObj["name"], view=f, name=urlObj["name"])
    urlpatterns.append(p)
    #p = path(urlObj["name"]+'/', view=f, name=urlObj["name"])
    #urlpatterns.append(p)

