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

Test
----

Start a mongod instance on port ``27017``.

Run ``py.test test.py``.


Usage
-----

.. code-block:: bash

    $ mongodbbackup --help

Make sure which ``mongod`` instance you want to backup, and run
``mongodbbackup`` on that server.

Example
^^^^^^^

* Backup a standalone mongod instance.

  .. code-block:: bash

    $ mongodbbackup -p <port> --primary-ok <backup_dir>

  **Caution:** it will block all writes.

* Backup a replication, run the follow command on a secondary server.

  .. code-block:: bash

    $ mongodbbackup -p <secondary_port> <backup_dir>

* Backup a cluster, backup a config server and each shard. If you have
  two shards, you need to run the follow command three times.

  .. code-block:: bash

    $ mongodbbackup --ms-url <mongos_url> -p <port> <backup_dir>


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
data directory, you can copy back the data to restore if any disaster
happens.
