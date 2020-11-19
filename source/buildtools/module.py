from compiler import CompilerFlags

class Module(CompilerFlags):
    def __init__(self, name, type, private_defines, public_defines, private_includes, public_includes, cflags, ldflags, libs, deps):
        super().__init__(cflags, ldflags)
        self.__name = name
        self.__libs = libs
        self.__type = type
        self.__deps = deps
        #self.__unity_file_name = self.__name + '.unity.cpp'
        self.__ignore_files = []

        self.__private_includes = private_includes
        self.__public_includes = public_includes
        
        self.__private_defines = private_defines
        self.__public_defines = public_defines

        """
        self.__object_file_name = self.__name + '.unity.o'

        if type == 'launcher':
            self.__bin_file_name = self.__name
        else:
            self.ldflags.append('-shared')
            self.__bin_file_name = 'lib' + self.__name + '.so'
        """

    @property
    def name(self):
        return self.__name
    
    """
    @property
    def unity_file_name(self):
        return self.__unity_file_name
    """
    
    """
    @property
    def object_file_name(self):
        return self.__object_file_name
    """

    """
    @property
    def bin_file_name(self):
        return self.__bin_file_name
    """

    @property
    def public_includes(self):
        return self.__public_includes
    
    @property
    def private_includes(self):
        return self.__private_includes
    
    @property
    def public_defines(self):
        return self.__public_defines
    
    @property
    def private_defines(self):
        return self.__private_defines
    
    @property
    def deps(self):
        return self.__deps
    
    @property
    def libs(self):
        return self.__libs

    @property
    def ignore_files(self):
        return self.__ignore_files

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        self.__type = type
