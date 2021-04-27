import sys
import os
import argparse
import pkgutil
import pkg_resources
from io import TextIOBase
from functools import wraps
from importlib import import_module

# import yzrpc
from yzrpc import __version__
from yzrpc.utils import get_abspath


class CommandError(RuntimeError):
    pass


class SystemCheckError(CommandError):
    pass


class CommandParser(argparse.ArgumentParser):
    """
    定制ArgumentParser类，改善错误消息输出的方式。
    """

    def __init__(self, *, missing_args_message=None,
                 called_from_command_line=None, **kwargs):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (self.missing_args_message and
                not (args or any(not arg.startswith('-') for arg in args))):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError("Error: %s" % message)


class OutputWrapper(TextIOBase):
    """
    标准输出的消息格式化
    """

    def __init__(self, out, style_func=None, ending='\n'):
        self._out = out
        self.style_func = None
        self.ending = ending

    @property
    def style_func(self):
        """消息格式化函数"""
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        """判断是否为标准输出，否则不执行样式函数"""
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        """判断是否为终端，无法判断时返回False"""
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg, style_func=None, ending=None):
        msg = msg if isinstance(msg, str) else str(msg)
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class CommandBase:
    description = ''
    epilog = ''  # 在 description 参数后显示额外的对程序的描述
    formatter_cls_name = 'HelpFormatter'

    def __init__(self, stdout=None, stderr=None, **kwargs):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        self._called_from_console = kwargs.get('called_from_console', None)

    def create_parser(self, prog_name, subcommand, **kwargs):
        """
        ArgumentParser参数：
            prog: 程序的名称（默认值：sys.argv[0]）
            usage: 描述程序用途的字符串（默认值：从添加到解析器的参数生成）
            description: 在参数帮助文档之前显示的文本（默认值：无）
            epilog: 在参数帮助文档之后显示的文本（默认值：无）
            parents: 一个 ArgumentParser 对象的列表，它们的参数也应包含在内
            formatter_class: 用于自定义帮助文档输出格式的类
            prefix_chars: 可选参数的前缀字符集合（默认值： '-'）
            fromfile_prefix_chars: 当需要从文件中读取其他参数时，用于标识文件名的前缀字符集合（默认值： None）
            argument_default: 参数的全局默认值（默认值： None）
            conflict_handler: 解决冲突选项的策略（通常是不必要的）
            add_help: 为解析器添加一个 -h/--help 选项（默认值： True）
            allow_abbrev: 如果缩写是无歧义的，则允许缩写长选项 （默认值：True）
        """
        parser = CommandParser(
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            # usage='%(prog)s [options]',
            description=self.description or None,
            formatter_class=self.select_formatter_cls(),
            missing_args_message=getattr(self, 'missing_args_message', None),
            called_from_command_line=getattr(self, '_called_from_console',
                                             None),
            **kwargs
        )
        parser.add_argument('-V', '--version', action='version',
                            version=self.get_version())
        parser.add_argument(
            '-v', '--verbosity', default=1,
            type=int, choices=[0, 1, 2, 3],
            help='Verbosity level; '
                 '0=minimal output, 1=normal output, '
                 '2=verbose output, 3=very verbose output',
        )
        self.add_arguments(parser)
        return parser

    def get_version(self):
        return pkg_resources.safe_version(__version__)

    def add_arguments(self, parser: argparse.ArgumentParser):
        """为子命令添加自定义参数"""
        pass

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, 
        derived from ``parser.usage``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def select_formatter_cls(self):
        """
        默认情况下，ArgumentParser 对象会将 description 和 epilog 的文字在命令行中自动换行。

        `RawDescriptionHelpFormatter` 和 `RawTextHelpFormatter` 
            在正文的描述和展示上给与了更多的控制:

        - `formatter_cls_name='RawDescriptionHelpFormatter'` 
            表示 description 和 epilog 已经被正确的格式化了，不能在命令行中被自动换行。

        - `formatter_cls_name='RawTextHelpFormatter'` 
            保留所有种类文字的空格，包括参数的描述。
            然而，多重的新行会被替换成一行。如果你想保留多重的空白行，可以在新行之间加空格。

        - `formatter_cls_name='ArgumentDefaultsHelpFormatter'` 
            自动添加默认的值的信息到每一个帮助信息的参数中.

        - `formatter_cls_name='MetavarTypeHelpFormatter'` 
            为它的值在每一个参数中使用 type 的参数名当作它的显示名（而不是使用常规的dest)
        """
        return getattr(argparse, self.formatter_cls_name)

    def execute(self, *args, **kwargs):
        """"""
        if kwargs.get('stdout'):
            self.stdout = OutputWrapper(kwargs['stdout'])
        if kwargs.get('stderr'):
            self.stderr = OutputWrapper(kwargs['stderr'],
                                        self.stderr.style_func)

        output = self.handle(*args, **kwargs)
        if output:
            self.stdout.write(output)
        return output

    def handle(self, *args, **options):
        """
        命令的实际逻辑。子类必须实现此方法。
        """
        raise NotImplementedError(
            'subclasses of CommandBase must provide a handle() method')


# ===============================================
# ---目前只做即时查询---
# 不对命令子类或名称做缓存，因为命令的使用并不频繁，
# 而且执行查找的速度并非不能接受。
# ===============================================

class CommandUtility:
    def __init__(self, command_dir=None, module_path=None):
        self.command_dir = get_abspath(command_dir) if command_dir else None
        self.module_path = module_path

    @staticmethod
    def load_command_cls(module_name, pkg_name='yzrpc', module_path=None):
        if module_path:
            module = import_module("%s.%s" % (module_path, module_name))
        else:
            module = import_module("%s.commands.%s" % (pkg_name, module_name))
        return module.Command

    @staticmethod
    def load_command_func(module_name, pkg_name='yzrpc', module_path=None):
        if module_path:
            module = import_module("%s.%s" % (module_path, module_name))
        else:
            module = import_module("%s.commands.%s" % (pkg_name, module_name))
        if hasattr(module, 'handle'):
            func = getattr(module, 'handle')
        elif hasattr(module, module_name):
            func = getattr(module, module_name)
        else:
            raise CommandError('Not found this function')
        return func

    def find_command(self, command_dir, command_name):
        """提供一个存放命令类的文件夹，查找该文件夹下符合条件的命令"""
        for _, name, is_pkg in pkgutil.iter_modules([command_dir]):
            if is_pkg or name.startswith('_'):
                continue
            if name == command_name:
                try:
                    _cmd = CommandUtility.load_command_cls(
                        command_name, module_path=self.module_path)
                    isfunc = False
                except Exception as e:
                    print(e)
                    _cmd = CommandUtility.load_command_func(
                        command_name, module_path=self.module_path)
                    isfunc = True
                return _cmd, isfunc
        raise CommandError(
            "Unknow command: %r in %s" % (command_name, command_dir))

    def get_command(self, command_name, **kwargs):
        """优先从本地项目获取命令，找不到的话再从库里面查找命令。"""
        from yzrpc.config import settings
        if settings.is_configured and settings.command_path:
            # TODO 从本地项目加载命令
            self.command_dir = settings.command_path
            try:
                command, isfunc = self.find_command(self.command_dir,
                                                    command_name)
            except CommandError:
                pass
            else:
                return command, isfunc
        if self.command_dir is None:
            self.command_dir = __path__[0]
        command, isfunc = self.find_command(self.command_dir, command_name)
        return command, isfunc

    def call_command(self, command, **kwargs):
        if isinstance(command, CommandBase):
            # command_name = command.__class__.__module__.split('.')[-1]
            return command(**kwargs).execute(**kwargs)
        else:
            command_name = command
            command, isfunc = self.get_command(command_name)

            if isfunc is False and isinstance(command, CommandBase):
                return command(**kwargs).execute(**kwargs)
            else:
                return command(**kwargs)

    def run_from_argv(self, argv):
        # prog_name = argv[0]
        try:
            subcommand = argv[1]
        except IndexError:
            subcommand = 'help'

        command, isfunc = self.get_command(subcommand)
        if isfunc is False:
            command = command(called_from_console=True)
            parser = command.create_parser(argv[0], subcommand)
            options, _args = parser.parse_known_args(argv[2:])
            cmd_options = vars(options)
            command.execute(*_args, **cmd_options)
        else:
            command(argv[2]) if len(argv) > 2 else command()

        # TODO help


class CmdDecorator:
    """
    Usage:
        >>> from yzrpc.commands import cmd

        >>> @cmd.run
        ... @cmd.attribute(description='This is a description.')
        ... @cmd.attribute(epilog='This is an epilog.')
        ... @cmd.argument('name')
        ... @cmd.argument('sub')
        ... def handle(*args):
        ...     print('Executing handle().')
        ...     print(args)
        ...
        ... handle('namexxx', 'subxxx')
    """

    def __init__(self, prog='yzrpc'):
        self._cmd_ins = CommandBase()
        self.prog = prog
        self.parser = None

    def run(self, subcommand):
        self.subcmd = subcommand
        self.parser = None

        def decorator(func):
            @wraps(func)
            def wrapper(*argv):
                self._cmd_ins.handle = func
                if self.parser is None:
                    self.parser = self._cmd_ins.create_parser(self.prog,
                                                              self.subcmd)
                options, _args = self.parser.parse_known_args(argv)
                cmd_options = vars(options)
                return self._cmd_ins.execute(*_args, **cmd_options)

            return wrapper

        return decorator

    def attribute(self, **kwargs):
        if self.parser:
            raise SystemCheckError(
                "'attribute' must be set before 'argument'.")
        for k in kwargs:
            setattr(self._cmd_ins, k, kwargs[k])

        def wrapper(func):
            return func

        return wrapper

    def argument(self, *args, **kwargs):
        if self.parser is None:
            self.parser = self._cmd_ins.create_parser(self.prog, self.subcmd)
        self.parser.add_argument(*args, **kwargs)

        def wrapper(func):
            return func

        return wrapper


cmd = CmdDecorator()



