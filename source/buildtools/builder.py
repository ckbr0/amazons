import sys
import platform
from pathlib import Path
import pickle
import subprocess

import ninja_syntax

# Base paths
projectdir = Path.cwd()
sourcedir = Path(projectdir, 'source')
tmpdir = Path(projectdir, 'tmp')
bindir = Path(projectdir, 'bin')

# Host
host_platform = platform.system()
host_machine = platform.machine()

# Target
target_platform = sys.argv[1]
target_configuration = sys.argv[2]
target_name = sys.argv[3]

# Build dirs
builddir = tmpdir / target_platform / target_configuration
ninja_file = builddir / 'build.ninja'
outdir = bindir / target_platform

target_file = sorted(sourcedir.glob('*.target.py'))[0]

class Builder():
    def __init__(self, platform, configuration):
        self.__platform = platform
        self.__configuration = configuration
        self.__targets = {}
    
    @property
    def platform(self):
        return self.__platform

    @property
    def configuration(self):
        return self.__configuration

    def target(self, name, cflags=[], ldflags=[]):
        self.__targets[name] = Target(name, cflags, ldflags)
        return self.__targets[name]
    
    @property
    def targets(self):
        return self.__targets

class CompilerFlags():
    def __init__(self, cflags, ldflags):
        self.__cflags = cflags
        self.__ldflags = ldflags

    @property
    def cflags(self):
        return self.__cflags

    @cflags.setter
    def cflags(self, flags):
        if self.__cflags is None:
            self.__cflags = []
        if isinstance(flags, str):
            self.__cflags.append(flags)
        elif isinstance(flags, list):
            self.__cflags += flags
        else:
            raise ValueError

    @property
    def ldflags(self):
        return self.__ldflags

    @ldflags.setter
    def ldflags(self, flags):
        if self.__ldflags is None:
            self.__ldflags = []
        if isinstance(flags, str):
            self.__ldflags.append(flags)
        elif isinstance(flags, list):
            self.__ldflags += flags
        else:
            raise ValueError

class Target(CompilerFlags):
    def __init__(self, name, cflags, ldflags):
        self._name = name
        super().__init__(cflags, ldflags)
        self.__modules = {}

    @property
    def modules(self):
        return self.__modules

    def module(self, name, type='default', cflags=[], ldflags=[], libs=[], deps=[]):
        self.__modules[name] = Module(name, type, cflags, ldflags, libs, deps)
        return self.__modules[name]

class Module(CompilerFlags):
    def __init__(self, name, type, cflags, ldflags, libs, deps):
        super().__init__(cflags, ldflags)
        self.__name = name
        self.__libs = libs
        self.__type = type
        self.__deps = deps
        self.__unity_file_name = self.__name + '.unity.cpp'

        if type == 'launcher':
            self.__bin_file_name = self.__name
            self.__object_file_name = self.__name + '.unity.o'
        else:
            self.ldflags = '-shared'
            self.__bin_file_name = 'lib' + self.__name + '.so'
            self.__object_file_name = self.__name + '.unity.o'

    @property
    def name(self):
        return self.__name
    
    @property
    def unity_file_name(self):
        return self.__unity_file_name

    @property
    def object_file_name(self):
        return self.__object_file_name
    
    @property
    def bin_file_name(self):
        return self.__bin_file_name
    
    @property
    def deps(self):
        return self.__deps

    @property
    def libs(self):
        return self.__libs

    @libs.setter
    def libs(self, libs):
        if self.__libs is None:
            self.__libs = []
        if isinstance(libs, str):
            self.__libs.append(libs)
        elif isinstance(libs, list):
            self.__libs += libs
        else:
            raise ValueError

    @property
    def ignore_files(self):
        return self.__ignore_files

    @ignore_files.setter
    def ignore_files(self, files):
        if self.__ignore_files is None:
            self.__ignore_files = []
        if isinstance(flags, str):
            self.__ignore_files.append(flags)
        elif isinstance(flags, list):
            self.__ignore_files += flags
        else:
            raise ValueError
    
    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        self.__type = type

builder = Builder(target_platform, target_configuration)
exec(target_file.open().read(), {'bld' : builder})

class Compiler():
    def __init__(self):
        pass

    def get_cxx(self):
        return 'gcc'

    def get_ar(self):
        return 'ar'

    def get_compile_rule(self):
        rule = {
            'command' : '$cxx -MMD -MT $out -MF $out.d $cflags -c $in -o $out',
            'description' : 'CXX $out',
            'depfile' : '$out.d',
            'deps' : 'gcc'
        }
        return rule

    def get_link_rule(self):
        rule = {
            'command' : '$cxx $ldflags -o $out $in $libs',
            'description' : 'LINK $out'
        }
        return rule

    def get_cflags(self):
        return ['-g', '-Wall', '-I'+str(gamedir), '-D_REENTRANT']

    def get_ldflags(self):
        return ['-Wall', '-L/usr/lib']

target_to_build = builder.targets[target_name]
modules_to_build = target_to_build.modules

compiler = Compiler()

builddir.mkdir(parents=True, exist_ok=True)
ninja_writer = ninja_syntax.Writer(ninja_file.open('w'))
n = ninja_writer

n.variable('ninja_required_version', '1.9')
n.newline()

n.variable('root', '.')
n.variable('builddir', builddir.relative_to(projectdir))
n.variable('bindir', outdir.relative_to(projectdir))

n.variable('cxx', compiler.get_cxx())
n.variable('ar', compiler.get_ar())
n.variable('cflags', ' '.join(target_to_build.cflags))
n.variable('ldflags', ' '.join(target_to_build.ldflags))

n.newline()

cxx_rule = compiler.get_compile_rule()
n.rule('cxx',
        command=cxx_rule['command'],
        depfile=cxx_rule['depfile'],
        deps=cxx_rule['deps'],
        description=cxx_rule['description'])
n.newline()
link_rule = compiler.get_link_rule()
n.rule('link',
        command=link_rule['command'],
        description=link_rule['description'])
n.newline()
n.rule('unity',
        command='python3 -B $root/source/buildtools/unity.py linux $in $out', 
        description='UNITY $out',
        restat=True)

n.newline()
n.comment('Modules')

for module in modules_to_build.values():
    n.newline()
    name = module.name
    n.comment(name)
    n.build(f'$builddir/' + module.unity_file_name,
            'unity',
            inputs='$root/source/' + module.name)
    n.build('$builddir/' + module.object_file_name,
            'cxx',
            inputs='$builddir/' + module.unity_file_name,
            variables={'cflags' : '$cflags ' + ' '.join(module.cflags)})
    n.build('$bindir/' + module.bin_file_name,
            'link',
            inputs='$builddir/' + module.object_file_name,
            variables={'ldflags' : '$ldflags ' + ' '.join(module.ldflags),
                'libs' : ' '.join(['-l' + x for x in module.deps + module.libs])},
                implicit=' '.join(['$bindir/' + modules_to_build[x].bin_file_name for x in module.deps]))

n.newline()
n.comment('Modules')

