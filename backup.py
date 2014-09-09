#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A tool to backup a mongodb cluster.

First stop balancer on mongos, and wait the running balancer
to stop, then fsync the mongod instance, and backup the dbpath.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from utils import Mongod, Mongos, rollover


@click.command()
@click.option('--ms-url', envvar='MONGOS_URL',
        help='Mongos url, used to stop and start balancer')
@click.option('--port', '-p', default=27017,
        help='The port mongod(need backup) listening on')
@click.option('--primary-ok', is_flag=True,
        help='Confirm to backup from primary')
@click.option('--backup-count', default=0,
        help='Number of backups to keep')
@click.argument('dst',
        type=click.Path(exists=True, file_okay=False, writable=True,
            resolve_path=True))
def main(ms_url, port, primary_ok, backup_count, dst):
    """MongoDB backup CLI

    DST: The directory to store backup data
    """
    # stop balancer and start balancer in the context manager
    with Mongos(ms_url):
        # backup mongod data
        mongod = Mongod(port)
        can_backup = False
        if not mongod.is_primary:
            can_backup = True
        elif not primary_ok:
            if click.confirm('This instance is primary,\n'
                    'it will block all writing when backuping,\n'
                    'do you want to continue?'):
                can_backup = True

        if can_backup:
            click.echo('Fsync mongod to stop writing......')
            mongod.fsync()
            click.echo('Begain copying dbpath......')
            mongod.backup_dbpath(dst)
            click.echo('Copy over!')

            # restore mongod and balancer
            mongod.unlock()
            # rollover
            rollover(dst, mongod.data_name, backup_count)
            click.echo('Done!')
        else:
            click.echo('Nothing to do!')
