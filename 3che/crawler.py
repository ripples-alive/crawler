#!/usr/bin/env python
#encoding:utf-8

import os
import sys
import requests

import MySQLdb
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

if len(sys.argv) != 4:
    print 'Invalid parameters!'
    exit(1)

print '=' * 60
print 'start:', sys.argv
aim_category_id = int(sys.argv[1])
start_point = (int(sys.argv[2]), int(sys.argv[3]))

immediate_download = False

base_url = 'http://www.3che.com'
session = requests.Session()

username = ''
password = ''

record = {
    'category': '',
    'detail_category': '',
    'post_url': '',
    'filename': '',
    'url': ''
}

sql_cnt = 0
connection = None
cursor = None
def record_to_mysql():
    global sql_cnt, connection, cursor
    if sql_cnt % 20 == 0:
        if connection:
            connection.commit()
            connection.close()
            cursor.close()
        connection = MySQLdb.connect(host='', user='', passwd='', db='', port=3306, charset='utf8')
        cursor = connection.cursor()
    sql_cnt += 1

    cursor.execute('insert into san_che(`category`, `detail_category`, `post_url`, `filename`, `url`) values (%s, %s, %s, %s, %s)',
        (record['category'], record['detail_category'], record['post_url'], record['filename'], record['url']))

def login():
    login_path = '/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
    session.post(base_url + login_path, {'username': username, 'password': password})

def enter_directory(name):
    if immediate_download:
        if not os.path.exists(name):
            os.mkdir(name)
        os.chdir(name)

def get_soup(url, parse_only=None):
    text = session.get(url).text
    return BeautifulSoup(text, 'lxml', parse_only=parse_only)

def download_file(url, filename):
    print 'Downloading:', filename, '=>', url
    record['url'] = url
    record['filename'] = filename
    if immediate_download:
        with open(filename, 'w') as fp:
            res = requests.get(url)
            fp.write(res.content)
            fp.close()
    else:
        record_to_mysql()

def crawl_file(url, filename):
    try:
        soup = get_soup(url, SoupStrainer(id='attachpayform'))
        attach_form = soup.find('form', id='attachpayform')
        link = attach_form.table.find_all('a')[-1]
    except Exception as e:
        print 'Error! file url:', url
    else:
        download_file(link['href'], filename)

# Crawl detail data of one post.
def crawl_detail(detail_category, title, detail_url):
    print '-' * 100
    print 'Crawling Post:', detail_category, title, '=>', detail_url
    record['detail_category'] = detail_category
    record['post_url'] = detail_url
    # Enter detail directory.
    enter_directory(detail_category)
    prefix = detail_url.rsplit('/', 1)[-1].split('.', 1)[0]
    enter_directory(prefix + title)

    soup = get_soup(detail_url, SoupStrainer('p', {'class': 'attnm'}))
    attnms = soup.find_all('p', {'class': 'attnm'})

    for attnm in attnms:
        url = '{0}/{1}'.format(base_url, attnm.a['href'])
        crawl_file(url, attnm.a.text.strip(u'[下载]'))

    # Leave detail directory.
    if immediate_download:
        os.chdir('../..')

# Crawl data of one category.
def crawl_category(category, list_url):
    print '=' * 100
    print 'Crawling category:', category, '=>', list_url
    record['category'] = category
    # Create corresponding directory and enter.
    enter_directory(category)

    cur_page_id = 0
    url = list_url
    while url is not None:
        cur_page_id += 1

        print 'Crawling page url:', url
        soup = get_soup(url, SoupStrainer('span'))
        xsts = soup.find_all('span', {'class': 'xst'})

        if cur_page_id >= start_point[0]:
            cur_in_page_id = 0
            for xst in xsts:
                cur_in_page_id += 1

                detail = xst.find('a', {'class': 'xst'})
                if cur_page_id > start_point[0] or cur_in_page_id >= start_point[1]:
                    crawl_detail(xst.em and xst.em.a.text or '', detail.text, detail['href'])

        page_footer = soup.find('span', id='fd_page_top')
        next_link = page_footer.label.next_sibling
        if next_link is not None:
            url = next_link['href']
        else:
            url = None

    # Leave the directory.
    if immediate_download:
        os.chdir('..')

if __name__ == '__main__':
    login()

    # Extract categories from home page.
    soup = get_soup(base_url, SoupStrainer(id='nv'))
    category_lis = soup.find('div', id='nv').ul.find_all('li')
    categories = map(lambda x: (x.a.text, x.a['href']), category_lis)
    categories = filter(lambda x: x[1] != '/', categories)

    crawl_category(categories[aim_category_id][0], categories[aim_category_id][1])
    # for category in categories:
        # crawl_category(category[0], category[1])
