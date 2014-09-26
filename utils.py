#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utils
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import glob
import time
from shutil import copytree, rmtree
import click

from pymongo import MongoClient


def tm_echo(msg, tm=None, **kargs):
    """Echo the message beginning with time"""
    tm = tm or time.strftime("%Y-%m-%d %H:%M:%S")
    click.echo('[{}] {}'.format(tm, msg), **kargs)


def rollover(backup_path, data_name, backup_count):
    """rollover, keep only specified count of backup datas.
    if backup_count is 0, keep all data.
    """
    backup_datas = glob.glob("{0}/{1}-[0-9]*_[0-9]*".format(
        backup_path, data_name))
    backup_datas.sort()
    for data in backup_datas[:-backup_count]:
        rmtree(data)


class Mongos(object):
    """Used to stop and start balancer"""

    def __init__(self, url=None):
        self.conn = MongoClient(url) if url else None

    def set_balancer_state(self, running):
        """Set cluster balancer

        set_balancer_state(True) # start balancer
        set_balancer_state(False) # stop balancer
        """
        self.conn['config']['settings'].update(
                {'_id': "balancer"}, {'$set' : {'stopped': not running}},
                multi=True)

    def is_balancer_running(self):
        """Check whether balancer is still running"""
        lock = self.conn['config']['locks'].find_one({'_id': "balancer"})
        if lock and lock['state'] > 0:
            return True
        else:
            return False

    def __enter__(self):
        if self.conn:
            self.set_balancer_state(False)
            click.echo('Waiting for balancer to stop......')
            while self.is_balancer_running():
                time.sleep(10)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.set_balancer_state(True)


class Mongod(object):
    """Used to backup the mongo server data

    """

    def __init__(self, port):
        self.conn = MongoClient("mongodb://127.0.0.1:{0}".format(port))

    @property
    def dbpath(self):
        """Get db path from mongodb connection"""
        cmd_line_opts = self.conn['admin'].command('getCmdLineOpts')
        parsed = cmd_line_opts['parsed']
        if 'dbpath' in parsed:
            dbpath = parsed['dbpath']
        else:
            # MongoDB 2.6 has different structure
            dbpath = parsed['storage']['dbPath']
        return os.path.normpath(dbpath)

    @property
    def data_name(self):
        """return the mongod data directory name"""
        return os.path.basename(self.dbpath)

    @property
    def is_primary(self):
        """Check if this mongod is primary"""
        return self.conn.is_primary

    def fsync(self):
        """Lock write, and make sure all pending writes to datafile"""
        self.conn.fsync(lock=True)
        assert self.conn.is_locked
        j_dir = os.path.join(self.dbpath, 'journal')
        while os.listdir(j_dir):
            time.sleep(1)

    def unlock(self):
        """Unlock the mongodb server"""
        self.conn.unlock()
        assert not self.conn.is_locked

    def backup_dbpath(self, backup_path):
        """Copy mongodb dbpath to backup_path"""
        date_ext = time.strftime("%Y%m%d_%H%M%S")
        dst_data_name = "{0}-{1}".format(self.data_name, date_ext)
        copytree(self.dbpath, os.path.join(backup_path, dst_data_name))
