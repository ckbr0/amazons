import pathlib

class UnityFile():
    def __init__(self, module):
        if module.is_dir():
            self._module_dir = module
            self._module_name = module.stem()
            self._unity_file = 
