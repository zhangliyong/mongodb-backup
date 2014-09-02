#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A tool to backup a mongodb cluster.

First stop balancer on mongos, and wait the running balancer
to stop, then fsync the mongod instance, and backup the dbpath.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from utils import Mongod, Mongos


@click.command()
@click.option('--ms_url', envvar='MONGOS_URL',
        help='Mongos url, used to stop and start balancer')
@click.option('--port', '-p', default=27017,
        help='The port mongod(need backup) listening on')
@click.option('--primary-ok', is_flag=True,
        help='Confirm to backup from primary')
@click.argument('dst',
        type=click.Path(exists=True, file_okay=False, writable=True,
            resolve_path=True))
def main(ms_url, port, primary_ok, dst):
    """Entrance

    DST: The directory to store backup data
    """
    # stop balancer and start balancer in the context manager
    with Mongos(ms_url):
        # backup mongod data
        mongod = Mongod(port)
        can_backup = primary_ok
        if not primary_ok and mongod.is_primary:
            if click.confirm('This instance is primary, '
                    'it will block all writing when backuping, '
                    'do you want to continue?'):
                can_backup = True

        if can_backup:
            click.echo('Fsync mongod to stop writing......')
            mongod.fsync()
            click.echo('Begain copying dbpath......')
            mongod.backup_dbpath(dst)

        # restore mongod and balancer
        mongod.unlock()

    click.echo('Over!')
