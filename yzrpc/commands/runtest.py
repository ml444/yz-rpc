import os
from yzrpc.commands import cmd


@cmd.run('test')
def runtest():
    import pytest
    paths = []
    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        if dirpath.endswith('__pycache__'):
            continue
        for fname in filenames:
            if fname.startswith('test'):
                paths.append(os.path.join(dirpath, fname))

    return pytest.main(paths)


if __name__ == '__main__':
    runtest()

