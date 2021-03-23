from argparse import ArgumentParser, BooleanOptionalAction

from trendy import process

parser = ArgumentParser(prog='trendy', description='command line thing')
parser.add_argument('inputfile')
parser.add_argument('--quite', action=BooleanOptionalAction, help='show calculation results')
parser.add_argument('--measure', nargs='?', choices=['method_lines', 'complexity', 'fan_out'])

process(parser.parse_args())
