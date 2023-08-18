from matplotlib import transforms
import pygame
import math
import numpy as np

class ViewportManager:
  def __init__(self, center, initial_scale = 1):
    self.center = center
    self.scale = initial_scale
    self.__update_transforms()

    self.dragging = False
    self.dirty_transforms = False

  def on_mouse_middle_btn_down(self):
    self.last_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    self.dragging = True

  def on_mouse_middle_btn_up(self):
    self.dragging = False

  def on_mouse_wheel(self, y):
    f = math.copysign(0.1, y)

    centered_pos = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(self.center)

    self.center -= centered_pos * f
    self.scale = self.scale * (1 + f)
    self.dirty_transforms = True
  
  def update(self):
    if self.dragging:
      pos = pygame.Vector2(pygame.mouse.get_pos())
      delta = pos - self.last_mouse_pos
      self.last_mouse_pos = pos

      self.center += delta

      if delta != (0, 0):
        self.dirty_transforms = True

    if self.dirty_transforms:
      self.__update_transforms()
      self.dirty_transforms = False

  def __update_transforms(self):
    self.__world_vector_to_viewport = transforms.Affine2D().scale(self.scale, -self.scale).rotate_deg(0)
    self.__world_point_to_viewport = self.__world_vector_to_viewport.frozen().translate(self.center[0], self.center[1])

    self.__viewport_vector_to_world = self.__world_vector_to_viewport.frozen().inverted()
    self.__viewport_point_to_world = self.__world_point_to_viewport.frozen().inverted()

  def world_point_to_viewport(self, pts):
    return self.__world_point_to_viewport.transform(pts)
  
  def viewport_point_to_world(self, pts):
    return self.__viewport_point_to_world.transform(pts)

  def world_vector_to_viewport(self, pts):
    return self.__world_vector_to_viewport.transform(pts)
  
  def viewport_vector_to_world(self, pts):
    return self.__viewport_vector_to_world.transform(pts)
  
  def world_size_to_viewport(self, size):
    return size * self.scale