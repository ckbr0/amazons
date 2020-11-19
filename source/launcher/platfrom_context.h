#ifndef PLATFORM_CONTEXT
#define PLATFORM_CONTEXT

struct platform_context
{
	int (*create_window)(char* name, int x, int y, int w, int h);
};

#endif
