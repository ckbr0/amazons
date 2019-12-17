import platform
import os
import pathlib

import ninja_syntax
import gen_unity_files

projectdir = pathlib.Path.cwd()
sourcedir = pathlib.Path(projectdir, 'source')
tmpdir = pathlib.Path(projectdir, 'tmp')
bindir = pathlib.Path(projectdir, 'bin')

gamedir = pathlib.Path(sourcedir, 'game')
launcherdir = pathlib.Path(sourcedir, 'launcher')

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

compiler = Compiler()

class UnityFile():
    def __init__(self, module):
        if module.is_dir():
            self._module_dir = module
            self._module_name = module.stem()
            self._unity_file = tmpdir / self._module_name / '.unity.c'
        else:
            self._module_dir = tmpdir / module
            self._module_name = module
            self._unity_file = tmpdir / module / '.unity.c'

        
    def get_source_files_from_module():
        return sorted(Path(self._module_dir).glob('*.c'))
     
