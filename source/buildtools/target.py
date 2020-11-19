from pathlib import Path

from compiler import CompilerFlags
from module import Module

class Target(CompilerFlags):
    def __init__(self, name, defines, includes, libs, cflags, ldflags, builder):
        super().__init__(cflags, ldflags)
        self.__name = name
        self.__modules = {}
        self.__defines = defines
        self.__includes = includes
        self.__libs = libs
        self.__builder = builder
        #self.__launcher_module = None
        #self.__game_module = None

    @property
    def name(self):
        return self.__name

    @property
    def modules(self):
        return self.__modules
    
    @property
    def defines(self):
        return self.__defines
    
    @property
    def includes(self):
        return self.__includes

    @property
    def libs(self):
        return self.__libs

    def module(self, name, type='default', private_defines=[], public_defines = [], private_includes=[], public_includes=[], cflags=[], ldflags=[], libs=[], deps=[]):
        assert not name in self.__modules, "Module %s already exists" % name
        self.__modules[name] = Module(name, type, private_defines, public_defines, private_includes, public_includes, cflags, ldflags, libs, deps)
        #if type == 'launcher':
        #    self.__launcher_module = self.__modules[name]
        #elif type == 'game':
        #    self.__game_module = self.__modules[name]
        return self.__modules[name]

    def module_directories(self, dirs):
        sourcedir = self.__builder.sourcedir
        for d in dirs:
            module_file = sourcedir / Path(d) / Path(d + '.module.py')
            exec(module_file.open().read(), {'bld' : self.__builder, self.__name : self})
