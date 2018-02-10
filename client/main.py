#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import requests
import json
import threading
from fuse import FUSE, FuseOSError, Operations

url = 'http://149.125.122.83:5000/API/'
NODEID = 'Vipuls-Macbook'


def create_and_run_thread(target, arguments):

    t = threading.Thread(target=target, args=arguments)
    t.start()


def send_request(full_url, body):
    headers = {'content-type': 'application/json'}

    print("Sending request to " + str(full_url) + " with body: " + str(body))
    response = requests.post(full_url, data=body, headers=headers)
    assert response.ok


def create_request_json():
    data = dict()
    data["nodeid"] = NODEID
    return data


def send_initialize_request():
    full_url = url + 'initialize'
    data = create_request_json()

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_create_request(full_path, mode, uid, gid):
    full_url = url + "create"

    data = create_request_json()
    data["path"] = str(full_path)
    data["mode"] = str(mode)
    data["uid"] = str(uid)
    data["gid"] = str(gid)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_write_request(path, size):
    full_url = url + "write"

    data = create_request_json()
    data["path"] = str(path)
    data["size"] = str(size)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_truncate_request(path, size):
    full_url = url + "truncate"

    data = create_request_json()
    data["path"] = str(path)
    data["size"] = str(size)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_chmod_request(path, mode):
    full_url = url + "chmod"

    data = create_request_json()
    data["path"] = str(path)
    data["mode"] = str(mode)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_chown_request(path, uid, gid):
    full_url = url + "chown"

    data = create_request_json()
    data["path"] = str(path)
    data["uid"] = str(uid)
    data["gid"] = str(gid)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_rename_request(old, new):
    full_url = url + "rename"

    data = create_request_json()
    data["old"] = str(old)
    data["new"] = str(new)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_mkdir_request(path, mode):
    full_url = url + "mkdir"

    data = create_request_json()
    data["path"] = str(path)
    data["mode"] = str(mode)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


def send_rmdir_request(path):
    full_url = url + "rmdir"

    data = create_request_json()
    data["path"] = str(path)

    request_body = json.dumps(data)
    send_request(full_url, request_body)


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)

        print("Chmod function called")
        create_and_run_thread(send_chmod_request, (path, mode))

        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)

        print("Chown function called")
        create_and_run_thread(send_chown_request, (path, uid, gid))

        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)

        print("Rmdir function called")
        create_and_run_thread(send_rmdir_request, (path))

        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        print("Mkdir function called")
        create_and_run_thread(send_mkdir_request, (path, mode))

        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):

        print("Rename called")
        create_and_run_thread(send_rename_request, (old, new))

        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)

        to_return = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

        print("Create function called")
        uid = os.stat(full_path).st_uid
        gid = os.stat(full_path).st_gid
        create_and_run_thread(send_create_request, (path, mode, uid, gid))

        return to_return

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):

        print("Write function called")
        size = len(buf)
        create_and_run_thread(send_write_request, (path, size))
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)

        print("Truncate function called")
        size = length
        create_and_run_thread(send_truncate_request, (path, size))

        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    print("Starting fuse...")
    create_and_run_thread(send_initialize_request(), ())

    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])