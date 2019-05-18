import hashlib
import logging
import os
import subprocess
import sys
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
SITE = os.environ['SITE']


def add_torrents():
    headers = {'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 '
        'Chrome/73.0.3683.86 Safari/537.36')}
    session = requests.Session()
    session.headers.update(headers)

    resp = session.post(
        f'{SITE}/login.php',
        data={'nev': USERNAME, 'pass': PASSWORD,
              'submitted': 1, 'set_lang': 'hu'},
    )
    assert resp.status_code == 200

    resp = session.get(f'{SITE}/hitnrun.php')
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.content, features='lxml')

    links = []
    for div in soup.findAll('div', class_='hnr_tname'):
        links.append(div.find('a')['href'])

    cnt = len(links)
    logger.info("Numer of torrents: %d", cnt)

    torrents = []
    for idx, link in enumerate(links, 1):
        resp = session.get(f'{SITE}/{link}')
        soup = BeautifulSoup(resp.content, features='lxml')
        a = soup.select_one('a[href^=torrents\.php\?action\=download]')['href']

        content = session.get(f'{SITE}/{a}').content
        filename = hashlib.md5(content).hexdigest()
        torrent_path = f'/srv/torrent/watch/{filename}.torrent'
        with open(torrent_path, "wb") as t:
            t.write(content)

        torrents.append(torrent_path)

        logger.info('%d/%d\t%s', idx, cnt, torrent_path)
        time.sleep(0.5)

    # with directory watch this is not needed
    # output = subprocess.check_output(['deluge-console', 'add', *torrents])


if __name__ == "__main__":
    add_torrents()
