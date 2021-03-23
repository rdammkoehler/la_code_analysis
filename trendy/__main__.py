from argparse import ArgumentParser

from trendy import process

parser = ArgumentParser(description='command line thing')
parser.add_argument('inputfile')

args = parser.parse_args()

process(args)
