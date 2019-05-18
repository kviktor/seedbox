"""
this is not usedd atm
"""
import os

from rtorrent_xmlrpc import SCGIServerProxy
from xmlrpc.client import MultiCall


def to_mb(size):
    return '%.2f' % (size / 1024 / 1024)


server = SCGIServerProxy('scgi:///tmp/rtorrent-rpc.socket')
total_size = 0
downloading_size = 0
print('Download rate:', server.get_down_rate())
for h in server.download_list():
    name = server.d.get_name(h)
    size = server.d.get_size_bytes(h)
    total_size += size
    base_path = server.d.get_base_path(h)
    print(h[:5], name, to_mb(size), "MB")

    for n in range(server.d.get_size_files(h)):
        name = server.f.get_path(h, n)
        size = server.f.get_size_bytes(h, n)
        chunks = server.f.get_completed_chunks(h, n)
        total_chunks = server.f.get_size_chunks(h, n)
        percentage = int(chunks/total_chunks * 100)

        if size > 1024 * 1024 * 1024:
            server.f.set_priority(h, n, 0)
            full_path = os.path.join(base_path, name)
            if os.path.exists(full_path):
                os.unlink(full_path)
        else:
            downloading_size += size

        priority = server.f.get_priority(h, n)
        print(f"\t[{priority}] {name} - {to_mb(size)}MB - {percentage}%")


mc = MultiCall(server)
mc.get_up_rate()
mc.get_down_rate()
up_rate, down_rate = mc()

print(f"total size: {to_mb(total_size)}MB")
print(f"downloading size: {to_mb(downloading_size)}MB")
