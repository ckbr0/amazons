#include <SDL2/SDL.h>
#include <SDL2/SDL_vulkan.h>
#include "engine/game_context.h"

#define MB 1024000

void (*on_load)(game_context*);

int main(int argc, char* argv[])
{
	if (argc < 2)
	{
		SDL_LogCritical(SDL_LOG_CATEGORY_ERROR, "input game module");
		return 1;
	}

	SDL_LogSetAllPriority(SDL_LOG_PRIORITY_WARN);

	if (SDL_Init(SDL_INIT_EVERYTHING) != 0)
	{
		SDL_Log("Unable to initialize SDL: %s", SDL_GetError());
		return 1;
	}

	//printf("%s\n", argv[1]);

	game_context* game = (game_context*)malloc(sizeof(game_context));

	void* game_module_handel = SDL_LoadObject(argv[1]);
	if (game_module_handel == NULL)
	{
		SDL_LogCritical(SDL_LOG_CATEGORY_ERROR, "Unable to load game module: %s", SDL_GetError());
		return 1;
	}

	on_load = (void (*)(game_context*))SDL_LoadFunction(game_module_handel, "on_load");
	
	if (on_load != NULL)
	{
		on_load(game);
	}

	//game->init();
	
	void* mem_area = malloc(MB*50);

	SDL_Vulkan_LoadLibrary(NULL);

	SDL_Window *window;

	window = SDL_CreateWindow(
		"An SDL2 window",                  // window title
		SDL_WINDOWPOS_UNDEFINED,           // initial x position
		SDL_WINDOWPOS_UNDEFINED,           // initial y position
		640,                               // width, in pixels
		480,                               // height, in pixels
		SDL_WINDOW_VULKAN                  // flags - see below
	);

	// Check that the window was successfully created
	if (window == NULL) {
	    // In the case that the window could not be made...
		printf("Could not create window: %s\n", SDL_GetError());
		return 1;
    }

	// The window is open: could enter program loop here (see SDL_PollEvent())
	SDL_Delay(3000);  // Pause execution for 3000 milliseconds, for example

	// Close and destroy the window
	SDL_DestroyWindow(window);

	// Clean up
	SDL_Quit();

	return 0; 
}
