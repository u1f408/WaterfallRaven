import logging
from pathlib import Path
from argparse import ArgumentParser

from wfraven import __version__


cli = ArgumentParser()
cli.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
subparsers = cli.add_subparsers(dest="subcommand")


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """

    return (list(name_or_flags), kwargs)


def subcommand(args=[], parent=subparsers):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py subcommand -d
    """

    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator


def main():
    """Main entrypoint function, dispatching subcommands.
    """

    import wfraven.commands
    args = cli.parse_args()

    if args.subcommand is None:
        cli.print_help()
        return 1
    else:
        return args.func(args)
