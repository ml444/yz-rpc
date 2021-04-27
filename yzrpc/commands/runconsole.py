from . import cmd_manager
from yzrpc.server import Server
from yzrpc import current_app


@cmd_manager.cmd('console', aliases=['c'], help='Run Console')
def console():
    banner = """
        [Sea Console]:
        the following vars are included:
        `app` (the current app)
        """
    ctx = {'app': current_app}
    try:
        from IPython import embed
        h, kwargs = embed, dict(banner1=banner, user_ns=ctx, colors="neutral")
    except ImportError:
        import code
        h, kwargs = code.interact, dict(banner=banner, local=ctx)
    h(**kwargs)
    return 0