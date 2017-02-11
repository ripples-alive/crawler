# coding:utf-8

import os
import re
import time
import json
import random
import urllib
import logging
import tempfile
import argparse
import requests
import StringIO

import torndb
from fpdf import FPDF
from PIL import Image

from config import config


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
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116'


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
            res = session.get(url, headers=headers, timeout=10, proxies=session.proxies)
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
            if res.status_code == 500 and '你所查询的页面不存在' in res.content:
                raise DownloadError(404, '404 not found: {}'.format(res.url))
            return res


def single_download(stop_id, last_id=None):
    if last_id is None:
        last_id = stop_id - 1

    sql = 'SELECT * FROM it168_document WHERE id > %s AND id <= %s ORDER BY id LIMIT 1'
    paper = db.get(sql, last_id, stop_id)
    if paper is None:
        return stop_id

    try:
        log.info('downloading: %d %s', paper['id'], paper['title'])
    except Exception as e:
        log.info('downloading: %d', paper['id'])
    directory = os.path.join('files', *json.loads(paper['classification']))
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        res = get_response(paper['post_url'])
        hf_view = re.search('="hf_view"\s*value="([^"]*)"', res.content).group(1)
        page_count = int(re.search('st_cp=(\d+)', res.content).group(1))
        if page_count == 0:
            raise DownloadError(800, 'no page exists')
        # if page_count > 1000:
        #     raise DownloadError(700, 'too many pages')

        img_list = []
        for i in xrange(0, page_count, 50):
            img_list_url = 'http://ajax.wenku.it168.com/ajax/ViewHandle.ashx?jsonpcallback=jsonp1473400701483&callback=jsonpcallback_GetImgs&k={}&cp={:d}'
            img_list_url = img_list_url.format(urllib.quote(hf_view), i // 50 + 1)
            res = get_response(img_list_url, headers={'Referer': paper['post_url']})
            img_list += re.search("'imgs':'([^']*)'", res.content).group(1).split(',')

        if len(img_list) != page_count:
            raise DownloadError(850, 'page count incorrect')
        log.info('page count: %d', page_count)
        res = get_response(img_list[0])
        img = Image.open(StringIO.StringIO(res.content))
        suffix = '.{}'.format(img.format.lower())
        pdf = FPDF(unit='pt', format=img.size)
        with log.progress('images downloaing') as p:
            for idx, img_url in enumerate(img_list):
                p.status('page: %d', idx)
                res = get_response(img_url)
                fp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
                fp.write(res.content)
                fp.close()
                pdf.add_page()
                pdf.image(fp.name, 0, 0)
                os.remove(fp.name)

        # disposition = res.headers['Content-Disposition'].decode('utf-8')
        # filename = re.search('filename="(.*)"', disposition).group(1).strip()
        # restrict filename length
        paper['title'] = paper['title'][:150]
        filename = u'{0[id]:d}-{0[title]}.pdf'.format(paper)
        # replace illegal characters in filename
        filename = re.sub(r'[\s\\/:*?"<>|]', '', filename)
        pdf.output(os.path.join(directory, filename), 'F')
        # with open(os.path.join(directory, filename), 'wb') as fp:
        #     fp.write(res.content)
        state = 1
        log.info('download succeeded')
    except DownloadError as e:
        state = e.code
        log.warning('%s -> %s', type(e), e.message)

    sql = 'UPDATE it168_document SET state = %s WHERE id = %s'
    db.update(sql, state, paper['id'])
    return paper['id']


def range_download(start_id, stop_id):
    last_id = start_id - 1
    while last_id < stop_id:
        last_id = single_download(stop_id, last_id)


def daemon_download(daemon_id, interval=60):
    db.update('UPDATE it168_document SET state = 0 WHERE state = %s', -daemon_id)
    while True:
        affected_rows = db.update(
            'UPDATE it168_document SET state = %s WHERE state = 0 LIMIT 1',
            -daemon_id)
        if affected_rows == 0:
            log.info('no document to download, sleep %ds...', interval)
            time.sleep(interval)
            continue
        # I know this is inefficient, but it's easy to realize.
        stdoc = db.get(
            'SELECT id FROM it168_document WHERE state = %s LIMIT 1', -daemon_id)
        single_download(stdoc['id'])


def init():
    global log, db
    log = logging.getLogger('crawl')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    from pwn import log
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
