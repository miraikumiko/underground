import argparse

args_parser = argparse.ArgumentParser(description='Available command line arguments')
args_parser.add_argument(
    '-U',
    '--username',
    type=str,
    default=None,
    dest='username',
    help='username of user'
)
args_parser.add_argument(
    '-E',
    '--email',
    type=str,
    default=None,
    dest='email',
    help='email of user'
)
args_parser.add_argument(
    '-P',
    '--password',
    type=str,
    default=None,
    dest='password',
    help='password of user'
)
args_parser.add_argument(
    '-A',
    '--active',
    action='store_true',
    dest='is_active',
    help='active user'
)
args_parser.add_argument(
    '-S',
    '--superuser',
    action='store_true',
    dest='is_superuser',
    help='super user'
)
args_parser.add_argument(
    '-V',
    '--verified',
    action='store_true',
    dest='is_verified',
    help='verified user'
)
args_parser.add_argument(
    '-C',
    '--checkout',
    action='store_true',
    dest='checkout',
    help='payment checkout'
)
args_parser.add_argument(
    '-X',
    '--expire',
    action='store_true',
    dest='expire',
    help='expire check'
)

args = args_parser.parse_args()
