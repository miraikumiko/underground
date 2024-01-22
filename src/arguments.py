import argparse

args_parser = argparse.ArgumentParser(description='Avaible command line arguments')
args_parser.add_argument(
    '-c',
    '--config',
    type=str,
    default='config.ini',
    dest='config',
    help='config file path'
)
args_parser.add_argument(
    '-l',
    '--log',
    type=str,
    default='logs.log',
    dest='log',
    help='log file path'
)
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

args = args_parser.parse_args()
