import os

from deluge_client import DelugeRPCClient

DELUGE_USERNAME = os.environ['DELUGE_USERNAME']
DELUGE_PASSWORD = os.environ['DELUGE_PASSWORD']
MAX_TORRENTS_SIZE = int(os.environ['MAX_TORRENTS_SIZE'])


client = DelugeRPCClient('127.0.0.1', 58846, DELUGE_USERNAME, DELUGE_PASSWORD)


def get_active_torrents_with_sizes():
    torrents = []
    total_size_sum = 0
    downloading_size_sum = 0

    torrents_dict = client.core.get_torrents_status({}, [])
    for _id, data in torrents_dict.items():
        priorities = list(data[b'file_priorities'])
        downloading_size = 0
        for f in data[b'files']:
            if priorities[f[b'index']] > 0:
                downloading_size += f[b'size']

        data[b'_id'] = _id
        data[b'downloading_size'] = downloading_size
        torrents.append(data)

        total_size_sum += data[b'total_size']
        downloading_size_sum += downloading_size

    return torrents, total_size_sum, downloading_size_sum


def is_over(size):
    return size > 1024 * 1024 * 1024 * MAX_TORRENTS_SIZE


def remove_old_torrents(torrents):
    downloading_size_sum = 0
    trimmed_torrents = []

    for data in torrents:
        seeding_time = data[b'seeding_time']
        active_time = data[b'active_time']
        name = data[b'name']

        # for partial downloads seeding_time remains 0
        if seeding_time > 4 * 24 * 60 * 60 or active_time > 6 * 24 * 60 * 60:
            print(f'Removing {name}')
            client.core.remove_torrent(data[b'_id'], True)
            continue

        priorities = list(data[b'file_priorities'])
        downloading_size = 0
        for f in data[b'files']:
            if priorities[f[b'index']] > 0:
                downloading_size += f[b'size']

        data[b'downloading_size'] = downloading_size
        trimmed_torrents.append(data)

        downloading_size_sum += downloading_size

    return trimmed_torrents, downloading_size_sum


def remove_big_files(torrents, downloading_size):
    torrents = sorted(torrents, key=lambda x: x[b'downloading_size'], reverse=True)

    downloading_size_cond = downloading_size
    for data in torrents:
        priorities = list(data[b'file_priorities'])
        for f in data[b'files']:
            size = f[b'size']
            if size > 1024 * 1024 * 1024:
                priorities[f[b'index']] = 0
                downloading_size_cond -= size

        client.core.set_torrent_options([data[b'_id']], {'file_priorities': priorities})

        if not is_over(downloading_size_cond):
            break


if __name__ == '__main__':
    torrents, total_size, downloading_size = get_active_torrents_with_sizes()

    if is_over(downloading_size):
        torrents, downloading_size = remove_old_torrents(torrents)

    if is_over(downloading_size):
        remove_big_files(torrents, downloading_size)
