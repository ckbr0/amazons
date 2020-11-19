#ifndef ENGINE_CONTEXT
#define ENGINE_CONTEXT

struct engine_context
{
	void (*init)(int *mem_arena);
	void (*handle_event)(int event);
	void (*update)(float);
	void (*destroy)();
};

#endif
