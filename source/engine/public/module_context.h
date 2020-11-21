#ifndef MODULE_CONTEXT
#define MODULE_CONTEXT

struct module_context
{
	void (*init)();
	void (*handle_event)(int event);
	void (*update)(float);
	void (*destroy)();
};

#endif

