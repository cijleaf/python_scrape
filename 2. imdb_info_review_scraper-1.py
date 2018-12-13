import requests
from lxml import html
import time
import json
import datetime
import MySQLdb

headers= {
    'Accept-Language':'en-GB,en;q=0.5'
}
def find_tt_by_name(name):
    fs = name[0]
    name = name.replace('-','').replace('.','').replace(' ','_').lower()
    url = 'https://v2.sg.media-imdb.com/suggests/%s/%s.json'
    res = requests.get(url%(fs.lower(),name.lower()))
    result = res.content.split('imdb$%s('%name)[1][:-1]
    return json.loads(result)

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')  

def get_reviews(tt):
    url = 'https://www.imdb.com/title/%s/reviews'%tt
    res = requests.get(url,headers=headers).content
    page = html.fromstring(res)
    rev_container = page.xpath('//div[@class="lister-item mode-detail imdb-user-review  collapsable"]/div[@class="review-container"]/div[@class="lister-item-content"]')[:2]
    reviews = []
    for rev in rev_container:
        title = rev.xpath('a[@class="title"]/text()')[0].strip()
        text = rev.xpath('div[@class="content"]/div[@class="text show-more__control"]/text()')[0]
        rating = rev.xpath('div[@class="ipl-ratings-bar"]/span[@class="rating-other-user-rating"]/span[1]/text()')[0]
        date = rev.xpath('div[@class="display-name-date"]/span[@class="review-date"]/text()')[0].split()
        uname = rev.xpath('div[@class="display-name-date"]/span[@class="display-name-link"]/a/text()')[0]
        date = datetime.datetime(int(date[2]),int(month_string_to_number(date[1])),int(date[0]))
        reviews.append([title,rating,text,date,uname])
    return reviews
    
def get_imdb_info(tt):
    url = 'https://www.imdb.com/title/%s/'%tt
    res = requests.get(url,headers=headers)
    img = find_tt_by_name(tt)['d'][0]['i'][0]#html.fromstring(d.page_source).xpath('//img[@class="pswp__img"]/@src')[0]
    page = html.fromstring(res.content)
    fname = page.xpath('//h1[@itemprop="name"]/text()')[0].strip()
    try:
        img_thumb = page.xpath('//div[@class="poster"]/a/img/@src')[0]
    except:
        img_thumb = ''
    try:
        lang = page.xpath('//div[@id="titleDetails"]/div[2]/a/text()')[0]
    except:
        lang=''
    try:
        cast = ', '.join(page.xpath('//td[@itemprop="actor"]/a/span/text()'))
    except:
        cast=''
    try:
        desc = page.xpath('//div[@class="summary_text"]/text()')[0].strip()
    except:
        desc=''
    try:
        rating = page.xpath('//span[@itemprop="ratingValue"]/text()')[0]
    except:
        rating=''
    try:
        director = page.xpath('//span[@itemprop="director"]/a/span/text()')
        if len(director)>1:
            director = ', '.join(director)
        else:
            director = director[0]
    except:
        director=''
    try:
        time_length = page.xpath('//time[@itemprop="duration"]/text()')[0].strip()
    except:
        time_length = ''
    try:
        genres = page.xpath('//span[@itemprop="genre"]/text()')
        if len(genres)>1:
            genres = ' | '.join(genres)
        else:
            genres = genres[0]
    except:
        genres = ''
    return fname,img,desc,cast,lang,rating,director,time_length,genres,img_thumb
def get_tt(name):
    res = find_tt_by_name(name)
    res = [x for x in s['d'] if x['id'][:2] == 'tt']
    if len(res)>0:
        return res
    else:
        return 0

def main():
    db = MySQLdb.connect(host="db-2sw53e15l.aliwebs.com",user="2sw53e15l",passwd="Sing_123",db="2sw53e15l",connect_timeout=20)
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM movies_to_update;')
    rows = cursor.fetchall()
    for row in rows:
        #print row
        tt = row['imdb_id']
        movie_id = row['movie_id']
        movie_name,image,desc,cast,lang,rating,director,time_length,genres,img_thumb = get_imdb_info(tt)
        reviews = get_reviews(tt)
        print movie_name
        cursor.execute("UPDATE movies set imdb_ratings='%s', Movie_name='%s', description='%s', director='%s', cast='%s', original_language='%s',length_of_movie='%s', genres='%s', poster_img_thumbnail='%s', poster_img='%s'  WHERE movies_id=%s;"%(rating,movie_name,desc,director,cast,lang,time_length,genres,img_thumb,image,movie_id))
        for rev in reviews:
            title,rating,text,date,uname = rev
            cursor.execute('SELECT * FROM reviews WHERE title="%s" AND movie_id="%s";'%(title.encode('utf-8'),movie_id))
            rows = cursor.fetchall()
            text = text.replace("'",'').replace('"','')
            if len(rows)>0:
                cursor.execute("UPDATE reviews set star_rating='%s',title='%s',comment='%s',date_added='%s' WHERE id='%s';"%(rating,title.encode('utf-8'),text.encode('utf-8'),'{:%Y-%m-%d %H:%M:%S}'.format(date).encode('utf-8'),rows[0]['id']))
            else:
                cursor.execute("""INSERT INTO reviews(`comment`,`star_rating`,`movie_id`,`title`,`date_added`,`user_id`) VALUES ('%s','%s','%s','%s','%s','4');"""%(text.encode('utf-8'),rating,movie_id,title.encode('utf-8'),'{:%Y-%m-%d %H:%M:%S}'.format(date).encode('utf-8')))
        db.commit()
    cursor.execute('TRUNCATE TABLE movies_to_update;')
    db.close()
main()