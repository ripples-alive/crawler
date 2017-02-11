# coding:utf-8

import argparse
import logging
import os
import re
import time
import urlparse
from config import config

import requests
import torndb


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class DownloadError(Error):

    def __init__(self, code, message):
        self.code = code
        self.message = message


class RangeListAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        res = []
        for one in values.split(','):
            if re.match(r'^\s*$', one) is not None:
                continue
            m = re.match(r'^\d+$', one)
            if m is not None:
                res.append(int(m.group(0)))
                continue
            m = re.match(r'^(\d+)-(\d+)$', one)
            if m is not None:
                res.append((int(m.group(1)), int(m.group(2))))
                continue
            raise argparse.ArgumentError(self, 'invalid range: {}'.format(one))
        setattr(namespace, self.dest, res)


def gen_session():
    global session
    session = requests.Session()
    session.cookies.update({
        'hXas_2132_saltkey': 'KjMz7F1A',
        'hXas_2132_lastvisit': '1479896516',
        'hXas_2132_auth': 'e608BORLeSxH6vZ4gBU%2FoujokP39ngOFXFDg02PelFeJL7KoCuAi2fOaIBYgbXvBFTeo5cso5a640SL3LAAPcuIW%2BQ',
        'hXas_2132_nofavfid': '1',
        'hXas_2132_home_diymode': '1',
        'hXas_2132_st_t': '37636%7C1479910002%7C3c8388b3b5e70d1c822f3ab4452040aa',
        'hXas_2132_forum_lastvisit': 'D_39_1479906049D_41_1479906696D_47_1479907564D_63_1479909524D_2_1479910002',
        'hXas_2132_ulastactivity': 'a753C3VJSrbSxAweSdYZwD7ASLHrk5WDMJXjoN58nEia4xB0rhch',
        'hXas_2132_visitedfid': '42D43D47D40D2D63D41D39',
        'hXas_2132_st_p': '37636%7C1479955254%7C7f9231ffde8186a42e367363bcd5ab37',
        'hXas_2132_viewid': 'tid_35438',
        'hXas_2132_smile': '1D1',
        'hXas_2132_seccode': '16.8a26d01f8d0c516f63',
        'hXas_2132_lip': '61.129.42.67%2C1479966530',
        'hXas_2132_creditnotice': '0D1D0D0D0D0D0D0D0D37636',
        'hXas_2132_creditbase': '0D1010282D0D0D0D0D0D0D0',
        'hXas_2132_creditrule': '%E4%B8%8B%E8%BD%BD%E9%99%84%E4%BB%B6',
        'hXas_2132_sid': 'h93eWz',
        'hXas_2132_checkpm': '1',
        'hXas_2132_sendmail': '1',
        'a8672_pages': '1',
        'a8672_times': '4',
        'hXas_2132_lastact': '1479966534%09forum.php%09attachment',
    })


def switch_proxy():
    global session
    gen_session()
    return # return to disable proxy

    proxy = requests.get('http://dynamic.goubanjia.com/dynamic/get/cfee1493c4b89a6a3d42e0e11551a922.html?ttl').content
    proxy = proxy.strip().split(',')
    log.info('switch proxy: %s', proxy)
    session.proxies = {
        'http': proxy[0],
    }
    try:
        log.info('IP: %s', session.get('http://members.3322.org/dyndns/getip').content.strip())
    except Exception as e:
        log.debug('proxy exception: %s -> %s', type(e), e.message)
        log.info('proxy unusable')
        switch_proxy()


def get_response(url, headers=None):
    global session
    timeout_cnt = 0
    failed_cnt = 0
    while True:
        try:
            res = session.get(url, headers=headers, timeout=30, proxies=session.proxies)
        except requests.exceptions.ConnectionError as e:
            switch_proxy()
        except requests.exceptions.ProxyError as e:
            switch_proxy()
        except requests.exceptions.ReadTimeout as e:
            timeout_cnt += 1
            if timeout_cnt >= 3:
                raise DownloadError(900, 'download timeout')
        except Exception as e:
            try:
                log.error('unknown error: %s -> %s', type(e), e.message)
            except Exception as e:
                pass
            failed_cnt += 1
            if failed_cnt >= 2:
                raise DownloadError(999, 'unknown error')
        else:
            if res.status_code == 404:
                raise DownloadError(404, '404 not found: {}'.format(res.url))
            return res


def single_download(stop_id, last_id=None):
    if last_id is None:
        last_id = stop_id - 1

    sql = 'SELECT * FROM daanjia_document WHERE id > %s AND id <= %s ORDER BY id LIMIT 1'
    document = db.get(sql, last_id, stop_id)
    if document is None:
        return stop_id

    try:
        log.info('downloading: %d %s', document['id'], document['filename'])
    except Exception as e:
        log.info('downloading: %d', document['id'])
    directory = os.path.join('files', document['directory'])
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        res = get_response(document['download_url'])
        direct_url = re.search(r"window\.location\.href\s*='(.*?)'", res.content).group(1)
        direct_url = urlparse.urljoin(document['download_url'], direct_url)

        res = get_response(direct_url)
        filename = u'{0[id]:d}-{0[filename]}'.format(document)
        # replace illegal characters in filename
        filename = re.sub(r'[\s\\/:*?"<>|]', '', filename)
        with open(os.path.join(directory, filename), 'wb') as fp:
            fp.write(res.content)

        state = 1
        log.info('download succeeded')
    except DownloadError as e:
        state = e.code
        log.warning('%s -> %s', type(e), e.message)

    sql = 'UPDATE daanjia_document SET state = %s WHERE id = %s'
    db.update(sql, state, document['id'])
    return document['id']


def range_download(start_id, stop_id):
    last_id = start_id - 1
    while last_id < stop_id:
        last_id = single_download(stop_id, last_id)


def daemon_download(daemon_id, interval=60):
    db.update('UPDATE daanjia_document SET state = 0 WHERE state = %s', -daemon_id)
    while True:
        affected_rows = db.update(
            'UPDATE daanjia_document SET state = %s WHERE state = 0 LIMIT 1',
            -daemon_id)
        if affected_rows == 0:
            log.info('no document to download, sleep %ds...', interval)
            time.sleep(interval)
            continue
        # I know this is inefficient, but it's easy to realize.
        stdoc = db.get(
            'SELECT id FROM daanjia_document WHERE state = %s LIMIT 1', -daemon_id)
        single_download(stdoc['id'])


def init():
    global log, db
    log = logging.getLogger('crawl')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    switch_proxy()
    db = torndb.Connection(
        config.get('database', 'host'),
        config.get('database', 'database'),
        user=config.get('database', 'user'),
        password=config.get('database', 'password'),
        max_idle_time=240)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', '--range', default=[], action=RangeListAction, help='download id range')
    parser.add_argument('-d', '--daemon', type=int, choices=xrange(1, 100), metavar='daemon_id',
        help='run as a daemon, use the specifc daemon id to identify')
    args = parser.parse_args()

    init()
    if args.daemon:
        daemon_download(args.daemon)
        exit()
    for r in args.range:
        if type(r) == int:
            single_download(r)
        else:
            range_download(r[0], r[1])
