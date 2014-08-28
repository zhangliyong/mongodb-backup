#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utils
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import time
from shutil import copytree
import click

from pymongo import MongoClient


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

    TODO: check if it's primary
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


    def fsync(self):
        """Lock write, and make sure all pending writes to datafile"""
        self.conn.fsync(lock=True)
        j_dir = os.path.join(self.dbpath, 'journal')
        while os.listdir(j_dir):
            time.sleep(1)

    def unlock(self):
        """Unlock the mongodb server"""
        self.conn.unlock()

    def backup_dbpath(self, backup_path):
        """Copy mongodb dbpath to backup_path"""
        data_dir = os.path.basename(self.dbpath)
        date_ext = time.strftime("%Y%m%d_%H%M%S")
        dst_data_dir = "{0}-{1}".format(data_dir, date_ext)
        copytree(self.dbpath, os.path.join(backup_path, dst_data_dir))
