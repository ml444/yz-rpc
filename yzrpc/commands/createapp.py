import os
import textwrap
import shutil
import stat

from jinja2 import Environment, FileSystemLoader

import yzrpc
from . import CommandBase, CommandError
from yzrpc.utils import get_abspath



class Command(CommandBase):
    formatter_cls_name = 'RawDescriptionHelpFormatter'
    description = textwrap.dedent('''\
        说明：
        --------------------------------
            示例：
            - 创建工程内部应用：
            ```shell
            $ cd my_project
            $ yzrpc createapp <app_name>
            ```
        ''')
    missing_args_msg = "You must provide a <app_name>."

    # 文件后缀替换
    rewrite_template_suffixes = (
        ('.tmpl', ''),
        # ('.ini.tmpl', '.ini'),
        # ('.md.tmpl', '.md'),
    )

    def add_arguments(self, parser):
        parser.add_argument('app_name', help='Name of the app.')
        parser.add_argument(
            '-D', '--destination',
            nargs='?', default='./src',
            help='Destination directory.'
        )
        parser.add_argument(
            '-T', '--template',
            help='The path or URL to load the template from.')
        parser.add_argument(
            '--render_ext', dest='render_exts',
            action='append', default=['tmpl'],
            help='The file extension(s) to render (default: "tmpl"). '
                 'Separate multiple extensions with commas.'
        )
        return super().add_arguments(parser)

    @staticmethod
    def _validate_app_name(proj_name):
        path, name = os.path.split(proj_name)
        if path:
            raise CommandError("The app name can't have a path; "
                               "please use the '-D' parameter for the path.")

    @staticmethod
    def _validate_target_dir(target_dir):
        if not os.path.exists(target_dir):
            raise CommandError("Destination directory {} does not exist, "
                               "please create it first.".format(target_dir))

    @staticmethod
    def _validate_template_dir(temp_dir):
        if not os.path.exists(temp_dir):
            raise CommandError("The template dir is not exist.")

    def handle(self, **options):
        app_name = options.get('app_name')
        self._validate_app_name(app_name)
        target_dir = options.get('destination')
        is_replace = False

        if target_dir is None:
            target_dir = os.getcwd()
        else:
            target_dir = os.path.abspath(os.path.expanduser(target_dir))
            self._validate_target_dir(target_dir)

        # 获取需要渲染的扩展名后缀
        # render_exts = options.get('render_exts')

        if options.get('template'):
            self.template_dir = get_abspath(options.get('template'))
            self._validate_template_dir(self.template_dir)
        # elif self.template_dir:
        #     pass
        else:
            self.template_dir = os.path.join(
                yzrpc.__path__[0], 'templates', 'app_template')

        # 定义模版环境并添加自定义函数
        env = Environment(loader=FileSystemLoader(self.template_dir))
        env.globals = env.make_globals({"camel_case": camel_case})
        for dirpath, dirnames, filenames in os.walk(self.template_dir):
            # 剔除不要的目录
            for dirname in dirnames[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirnames.remove(dirname)
            # 获取相对路径
            relative_dir = os.path.relpath(dirpath, self.template_dir)
            if relative_dir == '.':
                relative_dir = ''
            dst_dir = os.path.join(target_dir, relative_dir)
            # 替换app_name文件夹
            if dst_dir.endswith('app_name'):
                dst_dir = dst_dir.replace('app_name', app_name)

            try:
                os.makedirs(dst_dir)
            except FileExistsError:
                pass

            for filename in filenames:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    continue
                src_path = os.path.join(dirpath, filename)
                if filename.startswith('app_name'):
                    filename = filename.replace('app_name', app_name)
                dst_path = os.path.join(dst_dir, filename)
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if dst_path.endswith(old_suffix):
                        dst_path = dst_path[:-len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                if is_replace is False and os.path.exists(dst_path):
                    if self._called_from_console:
                        s = input(
                            f"'{filename}' already exists. replace? (y/n/all): ")
                        if s.lower() == 'all':
                            is_replace = True
                        elif s.lower() not in ['y', 'yes', 'true']:
                            continue
                    else:
                        raise CommandError(
                            "%s already exists, overlaying a project "
                            "into an existing directory won't replace "
                            "conflicting files" % dst_path)

                # 复制文件
                self.copy_file(
                    src_path, dst_path, env, **options)

    def copy_file(self, src_path, dst_path, env, **options):
        _, ext = os.path.splitext(src_path)
        if ext[1:] in options.get('render_exts'):
            self.template_copy_and_render(
                dst_path, src_path, env, **options)
        else:

            shutil.copyfile(src_path, dst_path)

        # if self.verbosity >= 2:
        self.stdout.write("Creating %s\n" % dst_path)
        try:
            shutil.copymode(src_path, dst_path)
            # 再次确保复制过来的文件具有可写权限
            self.make_writeable(dst_path)
        except OSError:
            self.stderr.write(
                "Notice: Couldn't set permission bits on %s." % dst_path)

    def template_copy_and_render(self, dst, src, env, **option):
        relative_src_path = os.path.relpath(src, self.template_dir)
        with open(dst, 'w') as f:
            tmpl = env.get_template(relative_src_path)
            f.write(tmpl.render(**option))

    def make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)


def camel_case(string, is_start_case=True):
    """
    将下划线命名转为驼峰命名
    :param string:
    :param is_start_case:
    :return:
    """
    s_list = string.split('_')
    res = ''
    for i in s_list:
        res += i.title()
    return res if is_start_case else res[0].upper() + res[1:]

'''
@cmd_manager.cmd('createproject', aliases=['n'], inapp=False, help='Create RPC Project')
@cmd_manager.option('project', help='project name')
@cmd_manager.option('--skip-git', action='store_true',
             help='skip add git files and run git init')
@cmd_manager.option('--skip-peewee', action='store_true', help='skip peewee')
@cmd_manager.option('--skip-cache', action='store_true', help='skip cache')
@cmd_manager.option('--skip-async-task', action='store_true', help='skip async_task')
@cmd_manager.option('--skip-bus', action='store_true', help='skip bus')
@cmd_manager.option('--skip-sentry', action='store_true', help='skip sentry')
def new(project, **extra):
    PACKAGE_DIR = os.path.dirname(__file__)
    TMPLPATH = os.path.join(PACKAGE_DIR, 'template')
    IGNORED_FILES = {
        'git': ['gitignore'],
        'peewee': ['configs/default/peewee.py.tmpl',
                   'app/models.py.tmpl'],
        'cache': ['configs/default/cache.py.tmpl'],
        'sentry': [],
        'async_task': ['configs/default/async_task.py.tmpl',
                       'app/tasks.py.tmpl'],
        'bus': ['configs/default/bus.py.tmpl', 'app/buses.py.tmpl'],
    }

'''