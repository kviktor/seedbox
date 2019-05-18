#!/bin/bash

USERNAME=''
PASSWORD=''
SITE=''

DELUGE_USERNAME=''
DELUGE_PASSWORD=''
MAX_TORRENTS_SIZE=70


echo "[+] Clearing watch directory"
rm -f /srv/torrent/watch/*.torrent
echo "[+] Done"

echo "[+] Running script"
USERNAME=$USERNAME PASSWORD=$PASSWORD SITE=$SITE python3.7 download_torrents.py
echo "[+] Done"

echo "[+] Grooming torrents"
DELUGE_USERNAME=$DELUGE_USERNAME DELUGE_PASSWORD=$DELUGE_PASSWORD MAX_TORRENTS_SIZE=$MAX_TORRENTS_SIZE python3.7 deluge_script.py
echo "[+] Done"
