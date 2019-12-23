import sys
from pathlib import Path
from hashlib import md5

#known_platforms = ['linux', 'win', 'android']

source_files = sorted(Path(sys.argv[2]).absolute().glob('*.c*'))
unity_file = Path(sys.argv[3])

new_unity_string = '\n'.join(map(lambda x: f'#include "{str(x)}"', source_files)).encode()
new_unty_hash = md5(new_unity_string).hexdigest()

unity_hash = None
if unity_file.is_file():
    unity_hash = md5(unity_file.read_bytes()).hexdigest()

if unity_hash != new_unty_hash:
    unity_file.write_bytes(new_unity_string)
    
