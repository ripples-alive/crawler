#!/usr/bin/env python
# encoding:utf-8

import os
import sys
import requests

import MySQLdb
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

from config import *

base_url = 'http://download.kaoyan.com'
status = []


def get_soup(url, parse_only=None):
    content = requests.get(url).content
    return BeautifulSoup(content, 'lxml', parse_only=parse_only)


def mysql_connect():
    global connection
    connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD,
                                 db=DB_DATABASE, port=3306, charset='utf8')


def mysql_disconnect():
    global connection
    connection.commit()
    connection.close()


def get_full_url(path):
    if path.startswith('/'):
        return base_url + path
    return base_url + '/' + path


def crawl_file(file_url):
    soup = get_soup(file_url)
    center_soup = soup.find('div', id='centers')
    form_soup = soup.find('form', id='downLoad')
    if center_soup is None or form_soup is None:
        print 'Error! file url:', file_url
        return
    status.append({
        'filename': center_soup.h2.text.strip(u'文件名：'),
        'url': get_full_url(form_soup['action'])
    })

    global connection
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO `kaoyan_file`(`post_id`, `filename`, `url`) VALUES (%s, %s, %s)',
        (status[0], status[1]['filename'], status[1]['url'])
    )
    cursor.close()

    status.pop()


def crawl_post(post_url):
    soup = get_soup(post_url, SoupStrainer('dl', {'class': 't_attachlist'}))
    file_list_soup = soup.find_all('dt')

    for file_soup in file_list_soup:
        crawl_file(get_full_url(file_soup.a['href']))


def crawl(start, stop):
    while True:
        mysql_connect()
        global connection
        cursor = connection.cursor()
        cursor.execute(
            'SELECT `id`, `post_url` FROM `kaoyan_post` WHERE `id` >= %s AND `id` <= %s ORDER BY `id` LIMIT %s',
            (start, stop, 10)
        )
        posts = cursor.fetchall()
        cursor.close()
        mysql_disconnect()

        if len(posts) == 0:
            break

        mysql_connect()
        for row in posts:
            print 'Crawling post:', row
            status.append(row[0])
            crawl_post(row[1])
            status.pop()
        mysql_disconnect()

        start = int(posts[-1][0]) + 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Invalid parameters!'
        exit(1)

    print '=' * 60
    print 'start:', sys.argv
    crawl(int(sys.argv[1]), int(sys.argv[2]))
