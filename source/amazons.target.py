
amazons = bld.target('amazons', ldflags=['-L$builddir', '-L$bindir', '\'-Wl,-rpath,$$ORIGIN\''])
amazons.cflags = ['-g', '-Wall', '-Wextra', '-Wno-deprecated', '-Wno-missing-field-initializers', \
    '-Wno-unused-parameter', '-fno-rtti', '-fno-exceptions', '-fvisibility=hidden', \
    '-pipe', '-O2', '-DNDEBUG', '-DDEBUG']

common = amazons.module(name='common', cflags=[], ldflags=[], libs=[])
launcher = amazons.module(name='launcher', type='launcher', cflags=['-I/usr/include/SDL2 -D_REENTRANT'], ldflags=['-I/usr/lib'], libs=['SDL2'], deps=['common'])
game = amazons.module(name='game', type='game', cflags=[], ldflags=[], libs=[], deps=['common'])

