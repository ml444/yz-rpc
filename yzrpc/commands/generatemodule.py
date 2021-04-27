import os
import re
import textwrap
from os.path import join, exists, isfile

from grpc_tools import protoc

from . import CommandBase, CommandError


class Command(CommandBase):
    formatter_cls_name = 'RawDescriptionHelpFormatter'
    description = textwrap.dedent('''\
            说明：
            --------------------------------
                示例：
                - 根据设定的路径搜寻protobuf文件自动生成py模块：
                ```shell
                $ cd my_project
                $ yzrpc generatemodule 
                ```
            ''')
    missing_args_msg = "You must provide any of proto file in './src/protos/'."

    def add_arguments(self, parser):
        parser.add_argument(
            '-I', '--proto_path',
            # required=True,
            action='append',
            # default=['./src/protos'],
            help="The directory where we will search for proto files"
        )
        parser.add_argument(
            '-O', '--output_dir',
            # required=True,
            # action='append',
            # default='./src/services',
            help="The directory where we will output the module files"
        )
        parser.add_argument(
            'protos',
            nargs='*',
            help='the proto files which will be compiled.'
            'the paths are related to the path defined in "-I"'
        )

    def _processing_proto_paths(self, paths):
        _paths = set()
        _protos = []
        for _path in paths:
            if not os.path.exists(_path):
                continue
            for file in os.listdir(_path):
                file_path = join(_path, file)
                if isfile(file_path) and file.endswith('.proto'):
                    _paths.add(_path)
                    _protos.append(file_path)

        if not _paths:
            if self._called_from_console:
                self.stderr.write("Not found any of proto file.")
                import sys
                sys.exit(1)
            else:
                raise CommandError("Not found any of proto file.")
        return _paths, _protos

    def _processing_module_import(self, path):
        """"""
        pattern = 'import .*_pb2 as .*__pb2'
        _compile = re.compile(pattern)
        for filename in os.listdir(path):
            if filename.endswith('_pb2_grpc.py'):
                file_path = join(path, filename)
                with open(file_path, 'r') as f:
                    content = f.read()
                with open(file_path, 'w') as f:
                    search_result = _compile.search(content)
                    if not search_result:
                        continue
                    match_str = search_result.group()
                    replace_str = f"from . {match_str}"
                    content = re.sub(pattern, replace_str, content)
                    f.write(content)
                    

    def handle(self, *args, **options):
        proto_path = options.get('proto_path')
        if not proto_path:
            proto_path = [join(os.getcwd(), 'src', 'protos')]
        proto_path, _protos = self._processing_proto_paths(proto_path)

        proto_out = options.get('output_dir')
        if not proto_out:
            proto_out = join(os.getcwd(), 'src', 'services')

        protos = options.get('protos', [])
        if not protos:
            protos = _protos

        # 添加gRPC官方proto文件路径
        offical_proto_path = os.path.join(
            os.path.dirname(protoc.__file__), '_proto')
        proto_path.add(offical_proto_path)
        proto_path_args = []
        for protop in proto_path:
            proto_path_args += ['--proto_path', protop]

        cmd = [
            'grpc_tools.protoc',
            *proto_path_args,
            '--python_out', proto_out,
            '--grpc_python_out', proto_out,
            *protos
        ]
        result = protoc.main(cmd)  # susscess:0  failure:1

        # 处理相对导入问题
        self._processing_module_import(proto_out)
        return result


