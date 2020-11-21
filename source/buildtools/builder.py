import sys
import os
import platform
from pathlib import Path
import pickle
import subprocess

import ninja_syntax
from compiler import Compiler
from target import Target
from module import Module
from define import create_defines_file

class Builder():
    def __init__(self, platform, configuration, sourcedir):
        self.__platform = platform
        self.__configuration = configuration
        self.__sourcedir = sourcedir
        self.__targets = {}
    
    @property
    def platform(self):
        return self.__platform

    @property
    def configuration(self):
        return self.__configuration
    
    @property
    def sourcedir(self):
        return self.__sourcedir

    def target(self, name, defines=[], includes=[], libs=[], cflags=[], ldflags=[]):
        self.__targets[name] = Target(name, defines, includes, libs, cflags, ldflags, self)
        return self.__targets[name]
    
    @property
    def targets(self):
        return self.__targets

if __name__ == '__main__':

    # Base paths
    projectdir = Path.cwd()
    sourcedir = Path(projectdir, 'source')
    tmpdir = Path(projectdir, 'tmp')
    bindir = Path(projectdir, 'bin')

    # Host
    host_platform = platform.system().lower()
    host_arch = platform.machine()

    # Target
    target_platform = sys.argv[1]
    target_configuration = sys.argv[2]
    target_name = sys.argv[3]

    # Build dirs
    builddir = tmpdir / target_platform / target_configuration
    ninja_file = builddir / 'build.ninja'
    outdir = bindir / target_platform

    # Find target files
    target_files = sorted(sourcedir.glob('**/*.target.py'))

    # Create Builder and execute target files
    builder = Builder(target_platform, target_configuration, sourcedir)
    for target_file in target_files:
        exec(target_file.open().read(), {'bld' : builder})

    # Set target and modules to build
    target_to_build = builder.targets[target_name]
    modules_to_build = target_to_build.modules

    # Create compiler
    compiler = Compiler(host_platform, host_arch, target_platform, target_configuration)

    # Create build.ninja file and ninja writer
    builddir.mkdir(parents=True, exist_ok=True)
    n = ninja_syntax.Writer(ninja_file.open('w'))
    
    n.variable('ninja_required_version', '1.10')
    n.newline()

    n.variable('root', f'{projectdir}')
    n.variable('builddir', f'$root/{builddir.relative_to(projectdir)}')
    n.variable('bindir', f'$root/{outdir.relative_to(projectdir)}')
    n.variable('sourcedir', f'$root/{sourcedir.relative_to(projectdir)}')

    n.newline()
    n.variable('cxx', compiler.get_cxx())
    n.variable('ar', compiler.get_ar())

    # Set build wide compiler flags
    cflags = ' '.join(compiler.get_cflags())
    cflags = f"{cflags} {' '.join(target_to_build.cflags)}"
    global_defines = compiler.get_defines()
    global_defines.extend(target_to_build.defines)
    includes = '{compiler.get_include_prefix()}'.join(target_to_build.includes)
    n.variable('cflags', f'{cflags} {includes}')

    # Set build wide linker flags
    ldflags = ' '.join(compiler.get_ldflags())
    ldflags = f"{ldflags} {' '.join(target_to_build.ldflags)}"
    libs = '{compiler.get_link_library_prefix()}'.join(target_to_build.libs)
    n.variable('ldflags', f'{ldflags} {libs}')

    n.newline()

    n.comment("Rules")
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
            command='python3 -B $root/source/buildtools/unity.py linux $out $in', 
            description='UNITY $out',
            restat=False)
    """
    n.rule('runner',
            command='python3 -B $root/source/buildtools/runner.py $in $module $out',
            description='RUNNER $out')
    """
    n.newline()
    n.comment('Modules')

    for module in modules_to_build.values():
        n.newline()
        n.comment(module.name)

        # Resolve explicit compiler and linker flags
        cflags = ' '.join(module.cflags)
        ldflags = ' '.join(module.ldflags)

        # Resolve defines
        defines = global_defines.copy()
        defines.extend(module.public_defines)
        defines.extend(module.private_defines)

        # Resolve includes
        includes = module.private_includes.copy()
        includes.extend(module.public_includes)

        # Resolve libs
        libs = module.libs.copy()

        # Reslove export define
        if not module.type == 'launcher':
            defines.append(f'{module.name.upper()}_API {compiler.get_export_define()}')

        # Resolv module dependencies
        for dep in module.deps:
            dep_module = modules_to_build[dep]

            defines.append(f'{dep.upper()}_API {compiler.get_import_define()}')
            includes.extend(dep_module.public_includes)
            libs.append(f'{dep_module.name}_{builder.configuration}')

        # Convert lists to strings
        include_prefix = compiler.get_include_prefix()
        includes_str = ' '.join(map(lambda x: f'{include_prefix}{x}', includes))
        link_libs_prefix = compiler.get_link_library_prefix()
        libs_str = ' '.join(map(lambda x: f'{link_libs_prefix}{x}', libs))

        # Define unity build files
        module_source_path = sourcedir / module.name
        unity_src_file_name = f'{module.name}.unity.cpp'
        unity_obj_file_name = f'{module.name}.unity.o'
        unity_input_files = sorted(module_source_path.glob('**/*.c*'))
        unity_input_files_str = list(map(lambda x: f'$sourcedir/{str(x.relative_to(sourcedir))}', unity_input_files))

        # Create defines file
        define_file_flag = compiler.get_force_include_flag()
        defines_file_name = f'{module.name}.defines.h'
        defines_file = builddir / defines_file_name
        create_defines_file(defines_file, defines)

        # Create unity file
        n.build(f'$builddir/{unity_src_file_name}',
                'unity',
                inputs=unity_input_files_str)

        # Compile files
        n.build(f'$builddir/{unity_obj_file_name}',
                'cxx',
                inputs=f'$builddir/{unity_src_file_name}',
                variables={'cflags' : f'$cflags {cflags} {includes_str} {define_file_flag} $builddir/{defines_file_name}'})

        # Link
        output_prefix = compiler.get_output_prefix(module.type)
        output_name = target_to_build.name if module.type == 'launcher' else module.name
        output_extension = compiler.get_output_extension(module.type)
        output_ldflag = compiler.get_output_ldflag(module.type)
        n.build(f'$bindir/{output_prefix}{output_name}_{builder.configuration}{output_extension}',
                'link',
                inputs=f'$builddir/{unity_obj_file_name}',
                variables={
                    'ldflags' : f'$ldflags {output_ldflag} {ldflags}',
                    'libs' : f'{libs_str}'},
                implicit='')

    n.newline()

