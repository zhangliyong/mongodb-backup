mongodb-backup
==============

Backup mongodb data by copy dbpath

.. image:: https://pypip.in/download/mongodb-backup/badge.svg
    :target: https://pypi.python.org/pypi/mongodb-backup/
    :alt: Downloads


Install
-------

.. code-block:: bash

    $ pip install mongodb-backup

Usage
-----

.. code-block:: bash

    $ mongodbbackup --help

Make sure which ``mongod`` instance you want to backup, and run
``mongodbbackup`` on that server.

Under The Hood
--------------
This tool backup mongodb by copying dbpath, so it must run on the same machine
with the mongod instance. 

1. Fsync the mongod instance to block all writes.
2. Copy the dbpath.
3. Unlock the mongod instance to accept writes.

If you want to backup a mongodb cluster, you should specify ``--ms-url``
option. It will stop balancer before backup, and restart balancer after backup.

**Caution:** This tool doesn't make a point-in-time backup, it just copy the
data directory, you can copy back the data to restore when some disasters
happen.
