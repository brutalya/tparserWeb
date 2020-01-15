import requests

from bs4 import BeautifulSoup as bs
from isodate import parse_duration

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}


def index(request):
    search=""
    torrents = []
    base_url = 'http://rutor.info/search/'
    if request.method == "POST":
        search = request.POST.get("search")
        base_url=base_url+search
        session = requests.Session()
        request1 = session.get(base_url, headers=headers)
        if request1.status_code == 200:
            soup = bs(request1.content, 'html.parser')
            divs = soup.find_all('tr', attrs={'class': 'gai', 'class': 'tum'})
            for div in divs:
                tds = div.find_all('td')
                aa = tds[1].find_all('a')
                torrents_data = {
                    'date': tds[0].text,
                    'title':aa[2].text,
                    'linkToSitePage':aa[2]['href'],
                    'magnet':aa[1]['href'],
                    'link': aa[0]['href']
                }
                torrents.append(torrents_data)
        context = {
            'search': search,
            'torrents':torrents
        }
    else:
        context = {
            'search': search
        }
    return render(request, "index.html", context)





