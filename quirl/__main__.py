#!/usr/bin/env python
"""
Main entry to Quirl command-line tool.
"""
import os
import sys
import click
import setproctitle

from quirl.version import version


@click.group(invoke_without_command=True)
@click.option('-V', '--version', is_flag=True, help="Show the version and exit.")
@click.pass_context
def cli(ctx, version):
    """
    Quirl CLI.
    """
    subcommand = ctx.invoked_subcommand
    
    if subcommand:
        # Set process name dynamically
        setproctitle.setproctitle(f"quirl-{subcommand}")
    
    if version:
        # Show the version
        click.echo(version)
    
    elif not ctx.invoked_subcommand:
        # Print usage if no subcommands are invoked
        click.echo(ctx.get_help())


if __name__ == "__main__":
    cli()