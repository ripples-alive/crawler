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


def crawl_post(url):
    status.append(url)

    global connection
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO `kaoyan_post`(`type`, `list_url`, `post_url`) VALUES (%s, %s, %s)',
        status
    )
    cursor.close()

    status.pop()


def crawl_list(list_id):
    soup = get_soup(base_url + '/list-%d' % list_id)
    thread_list = soup.find('div', attrs={'class': 'threadlist'})
    if thread_list is None:
        print 'List not exists:', base_url + '/list-%d' % list_id
        return

    user_info_list = soup.find('div', attrs={'class': 'userinfolist'})
    status.append('-'.join(user_info_list.span.get_text().split(u' » ')[2:]))

    url = base_url + '/list-%d' % list_id
    while url is not None:
        print 'Crawing list:', url
        status.append(url)
        soup = get_soup(url)

        table_dom = soup.find('div', attrs={'class': 'threadlist'}).table
        post_list_dom = table_dom.find_all('a')
        mysql_connect()
        for post_dom in post_list_dom:
            crawl_post(base_url + post_dom['href'])
        mysql_disconnect()

        status.pop()
        pages_dom = soup.find('div', {'class': 'pages'})
        if pages_dom is None:
            break
        next_dom = pages_dom.find('a', {'class': 'next'})
        if next_dom is None:
            break
        url = base_url + next_dom['href']

    status.pop()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Invalid parameters!'
        exit(1)

    print '=' * 60
    print 'start:', sys.argv

    for i in xrange(int(sys.argv[1]), int(sys.argv[2]) + 1):
        crawl_list(i)
