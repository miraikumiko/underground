import argparse

args_parser = argparse.ArgumentParser(description='Available command line arguments')
args_parser.add_argument(
    '-e',
    '--email',
    type=str,
    default=None,
    dest='email',
    help='email of user'
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
    '-A',
    '--active',
    type=bool,
    default=True,
    dest='is_active',
    help='active user'
)
args_parser.add_argument(
    '-S',
    '--superuser',
    type=bool,
    default=False,
    dest='is_superuser',
    help='super user'
)
args_parser.add_argument(
    '-V',
    '--verified',
    type=bool,
    default=False,
    dest='is_verified',
    help='verified user'
)
args_parser.add_argument(
    '-c',
    '--checkout',
    action='store_true',
    dest='checkout',
    help='payment checkout'
)
args_parser.add_argument(
    '-E',
    '--expire',
    action='store_true',
    dest='expire',
    help='expire check'
)

args = args_parser.parse_args()
