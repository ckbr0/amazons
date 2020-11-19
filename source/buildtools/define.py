#import sys
#from pathlib import Path
from hashlib import md5

def create_defines_file(defines_file, defines):

    new_defines_string = '\n'.join(map(lambda x: f'#define {x}', defines)).encode()
    new_defines_hash = md5(new_defines_string).hexdigest()

    defines_hash = None
    if defines_file.is_file():
        defines_hash = md5(defines_file.read_bytes()).hexdigest()

    if defines_hash != new_defines_hash:
        defines_file.write_bytes(new_defines_string)
    
