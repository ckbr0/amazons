#include <SDL2/SDL.h>
#include "module_context.h"
#include "module_loader.h"

int load_module(char* module_name, void* module_handle, module_context* module)
{
	SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Loading module %s", module_name);

	module_handle = SDL_LoadObject(module_name);
	if (module_handle == NULL)
	{
		SDL_LogCritical(SDL_LOG_CATEGORY_ERROR, "Unable to load module: %s", SDL_GetError());
		return 1;
	}

	void (*on_load)(module_context*);
	on_load = (void (*)(module_context*))SDL_LoadFunction(module_handle, "on_load");
	if (on_load == NULL)
	{
		SDL_LogCritical(SDL_LOG_CATEGORY_ERROR, "Unable to load on_load function: %s", SDL_GetError());
		return 1;
	}
	
	on_load(module);

	return 0;
}
