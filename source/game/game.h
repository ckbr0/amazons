#ifndef GAME
#define GAME

struct game_context;

extern "C" __attribute__((__visibility__("default"))) void on_load(game_context* ctx);

#endif
