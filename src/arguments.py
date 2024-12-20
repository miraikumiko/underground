import argparse

args_parser = argparse.ArgumentParser(description='Available command line arguments')
args_parser.add_argument(
    '-c',
    '--checkout',
    type=str,
    default=None,
    dest='checkout',
    help='payment checkout'
)
args_parser.add_argument(
    '-e',
    '--expire',
    action='store_true',
    dest='expire',
    help='expire check'
)
args_parser.add_argument(
    '-m',
    '--migrate',
    action='store_true',
    dest='migrate',
    help='make sql tables'
)

args = args_parser.parse_args()
