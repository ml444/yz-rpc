import sys
from yzrpc.commands import CommandUtility


def main():
    cmd = CommandUtility()
    cmd.run_from_argv(sys.argv)


if __name__ == '__main__':
    main()


