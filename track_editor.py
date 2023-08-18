import pygame
from viewport_manager import ViewportManager
from path_manager import PathManager
from export_manager import ExportManager
from grid_draw import draw_grid
from hud import HudView, HudViewModel

VIEWPORT_SIZE = (1280, 720)

# pygame setup
pygame.init()

screen = pygame.display.set_mode(VIEWPORT_SIZE)
vm = ViewportManager((VIEWPORT_SIZE[0] * 0.2, VIEWPORT_SIZE[1] * 0.5), 30)
pm = PathManager(vm)
em = ExportManager(pm)

hud_view = HudView()
hud_vm = HudViewModel()

hud_view.bind(hud_vm)
hud_vm.bind(hud_view)

clock = pygame.time.Clock()
running = True

while running:
  # Forward events to components
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.MOUSEBUTTONDOWN:
      match event.button:
        case pygame.BUTTON_LEFT:
          pm.on_mouse_left_btn_down()
        case pygame.BUTTON_MIDDLE:
          vm.on_mouse_middle_btn_down()
        case pygame.BUTTON_RIGHT:
          pm.on_mouse_right_btn_down()
    
    if event.type == pygame.MOUSEBUTTONUP:
      match event.button:
        case pygame.BUTTON_LEFT:
          pm.on_mouse_left_btn_up()
        case pygame.BUTTON_MIDDLE:
          vm.on_mouse_middle_btn_up()

    if event.type == pygame.MOUSEWHEEL:
      vm.on_mouse_wheel(event.y)

    if event.type == pygame.KEYDOWN:
      match event.key:
        case pygame.K_c:
          pm.toggle_control()
        case pygame.K_s:
          em.save()

  # Logic
  vm.update()
  pm.update()

  hud_vm.yellow_cones_count = len(pm.right_cones)
  hud_vm.blue_cones_count = len(pm.left_cones)
  hud_vm.track_length = pm.track_length
  hud_vm.hairpin_radius = pm.hairpin_radius
  
  # Render
  screen.fill("black")
  draw_grid(vm, screen, VIEWPORT_SIZE, 1)
  pm.draw(screen)
  hud_view.draw(screen)

  # Commit
  pygame.display.flip()
  clock.tick(60)

pygame.quit()