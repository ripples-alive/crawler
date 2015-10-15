#!/usr/bin/env python
# encoding:utf-8

import requests

import MySQLdb
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from underscore import _


base_url = 'http://m.8dol.com'
cur_state = []


def record_store():
    print 'recoding...'
    connection = MySQLdb.connect(
        host='',
        user='',
        passwd='',
        db='',
        port=3306,
        charset='utf8'
    )
    cursor = connection.cursor()
    cursor.execute(
        'insert into eight_day(`city`, `region`, `school`, `area`, `building`, `student`, `cellphone`) value (%s, %s, %s, %s, %s, %s, %s)',
        (cur_state[0]['city'],
        cur_state[0]['region'],
        cur_state[0]['name'],
        cur_state[1]['area_name'],
        cur_state[2]['building_name'],
        cur_state[3]['store_user_name'],
        cur_state[3]['store_user_mobile'])
    )
    cursor.close()
    connection.commit()
    connection.close()


def craw_building(building_id):
    print 'Crawing building:', building_id
    res = requests.get(
        base_url + '/v2/nightStoreCommon/queryBuildingStoreList',
        params={'building_id': building_id}
    )
    stores = res.json()['data']

    for store in stores:
        cur_state.append(store)
        record_store()
        cur_state.pop()


def crawl_area(area_id):
    print 'Crawing area:', area_id
    res = requests.get(
        base_url + '/v2/nightStoreCommon/queryBuildingList',
        params={'area_id': area_id}
    )
    buildings = res.json()['data']

    for building in buildings:
        cur_state.append(building)
        craw_building(building['building_id'])
        cur_state.pop()


def crawl_parent_area(area_id):
    # crawl_area(area_id)
    print 'Crawing parent area:', area_id
    res = requests.get(
        base_url + '/area/query',
        params={'parent_id': area_id}
    )
    areas = res.json()['data']

    for area in areas:
        cur_state.append(area)
        crawl_area(area['area_id'])
        cur_state.pop()


if __name__ == '__main__':
    res = requests.get(base_url + '/api/store/list')
    data = _(res.json()['data']).chain()
    districts = data.map(lambda x, i, *a: x['districts']).flatten()
    places=districts.map(lambda x, i, *a: x['places']).flatten().value()

    for place in places:
        cur_state.append(place)
        crawl_parent_area(place['area_id'])
        cur_state.pop()
