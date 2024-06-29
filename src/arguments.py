import argparse

args_parser = argparse.ArgumentParser(description='Available command line arguments')
args_parser.add_argument(
    '-u',
    '--username',
    type=str,
    default=None,
    dest='username',
    help='username of user'
)
args_parser.add_argument(
    '-p',
    '--password',
    type=str,
    default=None,
    dest='password',
    help='password of user'
)
args_parser.add_argument(
    '-a',
    '--active',
    action='store_true',
    dest='is_active',
    help='active user'
)
args_parser.add_argument(
    '-c',
    '--checkout',
    action='store_true',
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
