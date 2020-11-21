#ifndef MODULE_LOADER
#define MODULE_LOADER

struct module_context;

int load_module(char* module_name, void* module_handle, module_context* module);

#endif
