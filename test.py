from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import shutil
import tempfile
import unittest
from click.testing import CliRunner
from utils import Mongod, tm_echo
import backup


def test_tm_echo(capsys):
    """Test tm_echo"""
    tm_echo('Hello', '2014-01-01: 00:00:00')
    out, _ = capsys.readouterr()
    assert out.strip() == '[2014-01-01: 00:00:00] Hello'


class MongodTestCase(unittest.TestCase):
    """TestCase for Mongod"""

    def setUp(self):
        self.mongod = Mongod(27017)

    def test_dbpath(self):
        """test dbpath"""
        self.assertTrue('journal' in os.listdir(self.mongod.dbpath))

    def test_fsync_and_unlock(self):
        """test fsync and unlock"""
        j_dir = os.path.join(self.mongod.dbpath, 'journal')
        self.mongod.fsync()
        self.assertFalse(os.listdir(j_dir))
        self.assertTrue(self.mongod.conn.is_locked)

        self.mongod.unlock()

    def test_backup_dbpath(self):
        """test backup_dbpath"""
        dst = tempfile.mkdtemp()
        self.assertFalse(os.listdir(dst))
        self.mongod.backup_dbpath(dst)
        self.assertTrue(os.listdir(dst)[0])
        shutil.rmtree(dst)

def test_cli():
    """test mongodbbackup -p <port> <dst> """
    dst = tempfile.mkdtemp()
    runner = CliRunner()
    result = runner.invoke(backup.main, ['-p', 27017, '--primary-ok', dst])
    assert result.exit_code == 0
    assert os.listdir(dst)[0]
    shutil.rmtree(dst)
