#ifndef GAME_CONTEXT
#define GAME_CONTEXT

struct game_context
{
	void (*init)();
	void (*handle_event)(int event);
	void (*update)(float);
	void (*destroy)();
};

#endif

