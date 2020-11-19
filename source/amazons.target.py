
amazons = bld.target('amazons', ldflags=['-L$builddir', '-L$bindir', '\'-Wl,-rpath,$$ORIGIN\''])
#amazons.cflags.extend(['-g', '-Wall', '-Wextra', '-Wno-deprecated', '-Wno-missing-field-initializers', \
#    '-Wno-unused-parameter', '-fno-rtti', '-fno-exceptions', '-fvisibility=hidden', \
#    '-pipe', '-O2', '-DNDEBUG', '-DDEBUG'])

amazons.module_directories([
    'launcher',
    'engine',
    'game'
    ])

