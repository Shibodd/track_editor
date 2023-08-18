import pygame
from viewport_manager import ViewportManager

def draw_grid(vm: ViewportManager, surface: pygame.Surface, viewport_size, grid_size):
  grid_size = vm.world_size_to_viewport(grid_size)

  MINOR_COLOR = pygame.Color(50, 50, 50)
  MINOR_WIDTH = 1
  
  MAJOR_COLOR = pygame.Color(70, 70, 70)
  MAJOR_WIDTH = 2

  x = vm.center[0] % grid_size
  while x < viewport_size[0]:
    pygame.draw.line(surface, MINOR_COLOR, (x, 0), (x, viewport_size[1]), width = MINOR_WIDTH)
    x += grid_size
  
  y = vm.center[1] % grid_size
  while y < viewport_size[1]:
    pygame.draw.line(surface, MINOR_COLOR, (0, y), (viewport_size[0], y), width = MINOR_WIDTH)
    y += grid_size

  pygame.draw.line(surface, MAJOR_COLOR, (vm.center[0], 0), (vm.center[0], viewport_size[1]), width = MAJOR_WIDTH)
  pygame.draw.line(surface, MAJOR_COLOR, (0, vm.center[1]), (viewport_size[0], vm.center[1]), width = MAJOR_WIDTH)