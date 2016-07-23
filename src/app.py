import datetime

import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup

from src.common.database import Database
from src.models.show import Show

app = Flask(__name__)
app.secret_key="tarun"
Database.initialize()

metacritic_link = 'http://www.metacritic.com/browse/tv/genre/date/{}?view=detailed&page={}'

def show_title(genre,page_no):
    title=[None]*30
    request = requests.get(metacritic_link.format(genre.replace(" ","").replace("&","").replace("or","").replace("%20",""), page_no), headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    content = request.content
    soup = BeautifulSoup(content, "html.parser")
# <div id="main" class="col main_col">
# <h3 class="product_title">
# <a href="/tv/vice-principals/season-1">
    soup2 = soup.find('div', {'id': 'main', 'class': 'col main_col'})

    elements = soup2.find_all('h3', {'class': 'product_title'})
    i=0
    for element in elements:
        title[i]=element.text
        i=i+1
    return title

#gfe_rd=cr&ei=Nv-NV73EHIbC8gfYrYH4CA&gws_rd=ssl,cr&fg=1
google_search_link='https://www.google.com/search?q={}+imdb'
def find_ratings(elements):
    rating=[None]*30
    i=0
    for element in elements:
        if element is not None:
            request = requests.get(google_search_link.format(element.replace(" ","+").replace("&","and")), headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko)"})

            content = request.content
            #print(content)
            soup = BeautifulSoup(content, "html.parser")
            #print(soup.prettify())
            #<div class="f slp">
            ratings=soup.find('div',{'class':'f slp'})
            #print(ratings)
            if ratings is not None:
                rating[i]=ratings.text
            else:
                rating[i]=" NA"
            i=i+1
        else:
            rating[i]=" NA"
            i=i+1
    return rating

youtube_link="https://www.youtube.com/results?search_query={}"
def find_trailer_link(elements):
    trailer_link=[None]*30
    i = 0
    for element in elements:
        if element is not None:
            request = requests.get(youtube_link.format(element.replace(" ", "+").replace("&", "and")), headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko)"})
            content = request.content
            soup = BeautifulSoup(content, "html.parser")

            #< h3 class ="yt-lockup-title contains-action-menu" >
            link_container=soup.find('h3', {'class':'yt-lockup-title'})

            link=link_container.find('a')
            part=link.get('href')
            trailer_link[i]="https://www.youtube.com"+part
            i=i+1
        else:
            trailer_link[i] = " #"
            i = i + 1
    return trailer_link


def show_release_date(genre, page_no):
    release_date = [None] * 30
    request = requests.get(
        metacritic_link.format(genre.replace(" ", "").replace("&", "").replace("or", "").replace("%20", ""), page_no),
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    content = request.content
    soup = BeautifulSoup(content, "html.parser")
    # <div id="main" class="col main_col">

    soup2 = soup.find('div', {'id': 'main', 'class': 'col main_col'})

    soup3 = soup2.find_all('li', {'class': 'stat release_date'})

    i = 0
    for element in soup3:
        date = element.find('span', {'class': 'data'})

        release_date[i] = date.text
        i = i + 1
    return release_date


def show_poster_link(genre, page_no):
    poster_link = [None] * 30
    request = requests.get(
        metacritic_link.format(genre.replace(" ", "").replace("&", "").replace("or", "").replace("%20", ""), page_no),
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    content = request.content
    soup = BeautifulSoup(content, "html.parser")
    # <div id="main" class="col main_col">

    soup2 = soup.find('div', {'id': 'main', 'class': 'col main_col'})

    soup3 = soup2.find_all('img')

    i = 0
    for element in soup3:
        poster_link[i] = element.get('src')
        i = i + 1
    return poster_link

def update_database(genre):


    show = Show(None, None, None, None, None)
    page_no = 0
    titles = show_title(genre, page_no)
    print(titles)
    ratings=find_ratings(titles)
    #print(ratings)
    trailers=find_trailer_link(titles)
    #print(trailers)
    release_dates=show_release_date(genre,page_no)
    poster_link=show_poster_link(genre,page_no)
    i=0
    while i<30:
        show._id=i+1
        show.title=titles[i]
        show.rating=ratings[i]
        show.trailer=trailers[i]
        show.release_date=release_dates[i]
        show.poster=poster_link[i]
        show.save_to_mongo(genre)
        i=i+1
    print("Database Updated")
    Database.remove_all(genre+"_last_updated")
    def json():                                 #can be removed, just done during testing something
        d = str(datetime.date.today())
        return {
            "last_updated_date": d
        }

    Database.insert(genre+"_last_updated", json())


genres=['action & adventure',
        'animation',
        'arts',
        'business',
        'comedy',
        'documentary',
        'drama',
        'educational',
        'events & specials',
        'fantasy',
        'food & cooking',
        'game show',
        'health & lifestyle',
        'horror',
        'kids',
        'movie / mini-series',
        'music',
        'news',
        'news / documentary',
        'reality',
        'science',
        'science fiction',
        'soap',
        'sports',
        'suspense',
        'talk & interview',
        'tech & gaming',
        'travel',
        'variety shows'
        ]

@app.route('/<string:genre>')
@app.route('/')
def home(genre = 'comedy'):



    #date=Database.find_coloumn(genre+'_last_updated','last_updated_date')


    #if Database.count_all(genre+'_last_updated') > 0:
    #    if date[0]['last_updated_date']!=str(datetime.date.today()):
    #       update_database(genre)
    #else:
    #    update_database(genre)

    #update_database(genre)
    print("Site Visited")
    t=Database.find_coloumn(genre,"title")
    new_title=[None]*30
    new_trailer = [None] * 30
    new_dates=[None]*30
    new_ratings=[None]*30
    new_poster_links=[None]*30

    i=0
    for title in t:
        new_title[i]=title['title']
        i=i+1
    i=0

    trailers = Database.find_coloumn(genre,"trailer")
    for trailer in trailers:
        new_trailer[i]=trailer['trailer']
        i=i+1

    i=0
    release_dates = Database.find_coloumn(genre, "release_date")
    for date in release_dates:
        new_dates[i] = date['release_date']
        i = i + 1

    i = 0
    ratings = Database.find_coloumn(genre, "rating")
    for rating in ratings:
        new_ratings[i] = rating['rating']
        i = i + 1

    i=0
    poster_links = Database.find_coloumn(genre, "poster")
    for poster_link in poster_links:
        new_poster_links[i] = poster_link['poster']
        i = i + 1


    return render_template('list.html', g_link='https://www.google.com/search?q=',elements=new_title, trailer_links=new_trailer,
                           genres=genres, current_genre=genre,
                           release_dates=new_dates,
                           ratings=new_ratings,
                           poster_links=new_poster_links)
