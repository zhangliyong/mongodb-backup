#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A tool to backup a mongodb cluster.

First stop balancer on mongos,
Then all the three hosts needed backup check the balance
status, if the balancer is running, sleep a while, and
check again, only when the balancer is stoped, the hosts
can backup the db directories.
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
@click.argument('dst',
        type=click.Path(exists=True, file_okay=False, writable=True,
            resolve_path=True))
def main(ms_url, port, dst):
    """Entrance

    DST: The directory to store backup data
    """
    # stop balancer and start balancer in the context manager
    with Mongos(ms_url):
        # backup mongod data
        mongod = Mongod(port)
        click.echo('Fsync mongod to stop writing......')
        mongod.fsync()
        click.echo('Begain copying dbpath......')
        mongod.backup_dbpath(dst)

        # restore mongod and balancer
        mongod.unlock()

    click.echo('Over!')
