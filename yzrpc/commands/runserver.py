import datetime

from yzrpc.server import Server
from yzrpc.commands import CommandBase
from yzrpc.utils import run_with_reloader, raise_last_exception


class Command(CommandBase):
    description = 'Run gRPC server'

    def add_arguments(self, parser):
        parser.add_argument(
            '-W', '--max_workers',
            type=int,
            help="Number of workers"
        )
        parser.add_argument(
            '-H', '--host',
            type=str,
            default='[::]',
            help="host to listen"
        )
        parser.add_argument(
            '-P', '--port',
            type=int,
            default=50051,
            help="Port number to listen"
        )
        parser.add_argument(
            '--async',
            action='store_true',
            default=False
        )
        parser.add_argument(
            '--autoreload',
            action='store_true',
            default=False
        )
        parser.add_argument(
            '--show-endpoints',
            action='store_true',
            default=True,
            help="Print all registered endpoints"
        )

    def handle(self, *args, **options):
        logo = """
         _  _  ____  ____  ____   ___ 
        ( \/ )(_   )(  _ \(  _ \ / __)
         \  /  / /_  )   / )___/( (__ 
         (__) (____)(_)\_)(__)   \___)
        """
        self.stdout.write(logo)
        if options['autoreload'] is True:
            self.stdout.write("ATTENTION! Autoreload is enabled!")
            run_with_reloader(self._handle, **options)
        else:
            self._handle(**options)

    def _handle(self, max_workers, host, port, *args, **kwargs):
        raise_last_exception()
        self.stdout.write("Starting server at %s" % datetime.datetime.now())

        server = Server(max_workers=max_workers,
                        host=host, port=port,
                        is_async=kwargs['async'])
        server.run()

        self.stdout.write("Server is listening port %s" % port)

        if kwargs['show_endpoints'] is True:
            self.stdout.write("Registered handlers:")
            for handler in self.extract_handlers():
                self.stdout.write("===> %s" % handler)

        server.wait_for_termination()

    def extract_handlers(self):
        from yzrpc.proto import __proto_meta__
        for app_name, proto in __proto_meta__.items():
            yield f"-------------->{app_name}<---------------"
            services = proto.services or []
            for svc in services:
                for method in svc.methods:
                    yield f"{svc.name}: {method.name}(" \
                        f"{method.request_cls.__name__}) -> " \
                        f"{method.response_cls.__name__}"

