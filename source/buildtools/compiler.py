class CompilerFlags():
    def __init__(self, cflags : list, ldflags : list):
        self.__cflags = cflags
        self.__ldflags = ldflags
 
    @property
    def cflags(self):
        return self.__cflags

    @property
    def ldflags(self):
        return self.__ldflags

class Compiler():
    def __init__(self, host_platform, host_arch, target_platform, configuration):
        self._host = host_platform
        self._host_arch = host_arch
        self._target = target_platform
        self._config = configuration

    def get_cxx(self):
        if 'linux' in self._host:
            return 'gcc'

    def get_ar(self):
        if 'linux' in self._host:
            return 'ar'

    def get_compile_rule(self):
        if self._host in ['linux']:
            return {
                'command' : '$cxx -MMD -MT $out -MF $out.d $cflags -c $in -o $out',
                'description' : 'CXX $out',
                'depfile' : '$out.d',
                'deps' : 'gcc'
            }

    def get_link_rule(self):
        if self._host in ['linux']:
            return {
                'command' : '$cxx $ldflags -o $out $in $libs',
                'description' : 'LINK $out'
            }

    def get_cflags(self):
        flags = []
        if self._host in ['linux']:
            flags.extend(['-Wall', '-Wextra', '-Wno-deprecated', '-Wno-missing-field-initializers', '-Wno-unused-parameter', '-fno-rtti', '-fno-exceptions', '-fvisibility=hidden', '-pipe'])
            if self._config == 'debug':
                flags.extend(['-g', '-O2'])
            return flags

    def get_defines(self):
        defines = []#['_REENTRANT']
        if self._config == 'debug':
            defines.append('DEBUG')

        return defines

    def get_ldflags(self):
        if 'linux' in self._host:
            return ['-Wall', '-L/usr/lib']

    def get_output_extension(self, module_type):
        if self._target in ['win64']:
            if module_type == 'launcher':
                return '.exe'
            elif module_type in ['default', 'game']:
                return '.dll'
            elif module_type in ['archive']:
                return '.lib'
        elif self._target in ['linux64', 'android']:
            if module_type == 'launcher':
                return ''
            elif module_type in ['default', 'game']:
                return '.so'
            elif module_type in ['archive']:
                return '.ar'

    def get_output_prefix(self, module_type):
        if self._target in ['linux64', 'android']:
            if module_type in ['default', 'game', 'archive']:
                return 'lib'
        return ''

    def get_output_ldflag(self, module_type):
        if self._target in ['linux64', 'android']:
            if not module_type == 'launcher':
                return '-shared'
        return ''

    def get_include_prefix(self):
        if self._target in ['linux64', 'android']:
            return '-I'

    def get_link_library_prefix(self):
        if self._target in ['linux64', 'android']:
            return '-l'
    
    def get_define_prefix(self):
        if self._target in ['linux64', 'android']:
            return '-D'

    def get_export_define(self):
        if self._target in ['linux64', 'android']:
            return '__attribute__((visibility("default")))'
        elif self._target in ['win64']:
            return '__declspec(dllexport)'
    
    def get_import_define(self):
        if self._target in ['linux64', 'android']:
            return ''
        elif self._target in ['win64']:
            return '__declspec(dllimport)'

    def get_force_include_flag(self):
        if self._target in ['linux64', 'android']:
            return '-include'
        elif self._target in ['win64']:
            return '/FI'
