import requests
import os
import sys
import getpass
import subprocess

from grab import Grab
from argparse import ArgumentParser
from colored import fg, attr
from bs4 import BeautifulSoup as bs
from django.shortcuts import render

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
            divs = soup.find_all('tr', attrs={'class': 'gai', 'class': 'tum'}) #parse torrents from rutor
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
        search=request.GET.get('search','spider')
        base_url = base_url + search
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
                    'title': aa[2].text,
                    'linkToSitePage': aa[2]['href'],
                    'magnet': aa[1]['href'],
                    'link': aa[0]['href']
                }
                torrents.append(torrents_data)
        context = {
            'search': search,
            'torrents': torrents
        }
    return render(request, "index.html", context)

def parseFromRutracker(search_name):
    parser = argument_parser()
    args = parser.parse_args()
    max_result = args.count
    no_download = args.no_download
    no_run_torrent = args.no_run_torrent

    grab = rutracker_auth()
    rutracker_data = parse_rutracker(grab, search_name, max_result)
    ##if not rutracker_data:


    ##for key in rutracker_data:


    rutracker_id = input_rutracker_id(max_result)
    url = rutracker_data[rutracker_id]['link']
    download_path = download_torrent(grab, search_name, url)


    subprocess.call(['xdg-open', download_path])
    return rutracker_data
####В ТУПУЮ ПИХНУЛ RUTRACKER DATA, нужно попробовать вывести оттуда данные на экран



RUTRACKER_FORUM = 'https://rutracker.org/forum'


def set_color(text, color='green'):
    return fg(color) + attr('bold') + text  + attr('reset')


def grab_go(grab, url):
    try:
        grab.go(url)
    except Exception as error:
        ##print error
        sys.exit(2)


def parse_rutracker(grab, search_text, max_result):
    rutracker_data = {}

    url = "{}/tracker.php?o=10&nm={}".format(RUTRACKER_FORUM, search_text)
    grab_go(grab, url)

    count = 0
    for item in grab.doc.select('//tr[@class="tCenter hl-tr"]'):
        seed  = item.select('.//td[@class="row4 nowrap"]/b').text()
        if int(seed) < 1:
            continue
        count += 1
        if count > max_result:
            break
        title = item.select('.//td[@class="row4 med tLeft t-title"]').text()
        size  = item.select('.//td[@class="row4 small nowrap tor-size"]').text()
        url   = "{}/{}".format(RUTRACKER_FORUM, item.select('.//td[@class="row4 med tLeft t-title"]/div/a').attr('href'))
        link  = "{}/{}".format(RUTRACKER_FORUM, item.select('.//td[@class="row4 small nowrap tor-size"]/a').attr('href'))
        size  = "{} {}".format(size.split()[1], size.split()[2])

        rutracker_data[count] = {'title': title, 'url': url, 'link': link, 'size': size, 'seed': seed}

    return rutracker_data


def rutracker_auth():
    fcookie = os.path.join(os.environ['HOME'], '.rutracker_cookies.txt')
    if not os.path.exists(fcookie):
        open(fcookie, 'w').close()

    grab = Grab(cookiefile=fcookie, connect_timeout=15, timeout=20)
    url = "{}/login.php".format(RUTRACKER_FORUM)
    grab_go(grab, url)

    if grab.doc.select('.//*[@name="login_username"]'):
        login = input("Username: ")
        password = getpass.getpass()
        grab.doc.set_input("login_username", login)
        grab.doc.set_input("login_password", password)
        grab.doc.submit()

    return grab


def download_torrent(grab, name, url):
    download_path = os.path.join(os.environ['HOME'], "[rutracker.org].{}.torrent".format(name))
    ##print "Download --> {}".format(download_path)

    grab_go(grab, url)
    grab.response.save(download_path)

    return download_path


def input_rutracker_id(max_result):
    try:
        rutracker_id = int(input(set_color('Dowload ID: ', color='blue')))
    except ValueError:
        ##print set_color('ERROR:', color='red'), "That was not a valid number\n"
        sys.exit(1)

    if rutracker_id > max_result:
        ##print set_color('ERROR:', color='red'), "Values for downloading should be less than the total number\n"
        sys.exit(1)

    return rutracker_id


def argument_parser():
    parser = ArgumentParser(description="Search and download torrents on the rutracker.org")
    parser.add_argument('name', metavar='SEARCH', help="Search query")
    parser.add_argument('-c', '--count', default=5, type=int, help="Max result")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-download', action='store_false', help="Only search torrents")
    group.add_argument('--no-run-torrent', action='store_false', help="Dowload without run client-torrent")

    return parser



# EOF

