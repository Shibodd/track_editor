import numpy as np
import splipy.curve_factory as cf
import pygame
import math

from dataclasses import dataclass
from viewport_manager import ViewportManager
import itertools


@dataclass
class PathKnot:
  position: pygame.Vector2
  control: pygame.Vector2

def knots_to_ctrl_points(knots: list[PathKnot]):
  return list(itertools.chain(
    (knots[0].position, knots[0].position + knots[0].control),
    itertools.chain.from_iterable((k.position - k.control, k.position, k.position + k.control) for k in knots[1:]),
    (knots[0].position - knots[0].control, knots[0].position)
  ))

def get_normal_vector2(tang):
  return np.cross(np.pad(tang, (0, 1), constant_values = 0), np.array([0, 0, 1]))[:-1]

def get_clicked_point(pos, pts, max_dist):
  dists = ((i, pos.distance_squared_to(x)) for i, x in enumerate(pts))
  close_enough = [(i, dist) for i, dist in dists if dist < max_dist ** 2]
  if len(close_enough) > 0:
    i, _ = min(close_enough, key = lambda t: t[1])
    return i
  return None

def get_cones(pts, max_distance):
  path_len = sum(pygame.Vector2(tuple(pts[i])).distance_to(pts[i + 1]) for i in range(len(pts) - 1))
  cones_count = math.ceil(path_len / max_distance)
  dist_between_cones = path_len / cones_count

  yield pts[0]

  t = 0
  c_idx = 0
  for i in range(len(pts) - 1):
    cur = pygame.Vector2(tuple(pts[i]))
    nex = pygame.Vector2(tuple(pts[i + 1]))

    l = cur.distance_to(nex)
    t += l
    if t >= dist_between_cones:
      c_idx += 1
      if c_idx >= cones_count:
        return
      excess = t - dist_between_cones
      t -= dist_between_cones

      fwd = (nex - cur).normalize()
      yield nex - fwd * excess
    
    


class PathManager:
  BOUNDARY_DISTANCE = 1.5
  CTRL_POINT_RADIUS = 5

  def __init__(self, vm: ViewportManager):
    self.vm = vm
    self.knots = [
      PathKnot(pygame.Vector2(0, 0), pygame.Vector2(0, 4)),
      PathKnot(pygame.Vector2(10, 0), pygame.Vector2(0, -4)),
    ]

    self.dragging_ctrl_idx = None
    self.control_enabled = True
    self.__update_curve()

  def get_centerline(self):
    return get_cones(self.approx_pts, 2)

  def toggle_control(self):
    self.control_enabled = not self.control_enabled
    self.dragging_ctrl_idx = None
    self.__update_curve()

  def __update_curve(self):
    self.ctrl_pts = knots_to_ctrl_points(self.knots)
    self.curve = cf.bezier(self.ctrl_pts)

    if self.control_enabled:
      precision = max(2, int(self.curve.length()))
    else:
      precision = max(2, int(self.curve.length() * 5))

    self.approx_pts = [self.curve(t) for t in np.linspace(self.curve.start(0), self.curve.end(0), precision)]

    gen = [(self.curve(t), self.BOUNDARY_DISTANCE  * get_normal_vector2(self.curve.tangent(t))) for t in np.linspace(self.curve.start(0), self.curve.end(0), precision)]
    self.right_wall = [ pos + norm for pos, norm in gen ]
    self.left_wall = [ pos - norm for pos, norm in gen ]

    if self.control_enabled:
      self.right_cones = self.left_cones = []
    else:
      self.right_cones = list(get_cones(self.right_wall, 3))
      self.left_cones = list(get_cones(self.left_wall, 3))

    self.track_length = self.curve.length()
    self.hairpin_radius = min([1 / self.curve.curvature(t) for t in np.linspace(self.curve.start(0), self.curve.end(0), precision)])

  def update(self):
    if self.dragging_ctrl_idx is not None:
      pos = self.vm.viewport_point_to_world(pygame.mouse.get_pos())

      knot_idx = math.floor((self.dragging_ctrl_idx + 1) / 3)
      if knot_idx >= len(self.knots):
        knot_idx = 0

      knot = self.knots[knot_idx]

      mod_idx = (self.dragging_ctrl_idx + 1) % 3
      match mod_idx:
        case 0:
          knot.control = knot.position - pos
        case 1:
          knot.position = pos
        case 2:
          knot.control = pos - knot.position
      
      self.__update_curve()

  def on_mouse_left_btn_down(self):
    if not self.control_enabled:
      return
    
    pos = pygame.Vector2(pygame.mouse.get_pos())
    i = get_clicked_point(pos, self.vm.world_point_to_viewport(self.ctrl_pts), PathManager.CTRL_POINT_RADIUS)
    if i is not None:    
      self.dragging_ctrl_idx = i

  def on_mouse_left_btn_up(self):
    self.dragging_ctrl_idx = None

  def on_mouse_right_btn_down(self):
    if not self.control_enabled:
      return
    
    pos = pygame.Vector2(pygame.mouse.get_pos())
    clicked_ctrl_i = get_clicked_point(pos, self.vm.world_point_to_viewport(self.ctrl_pts), PathManager.CTRL_POINT_RADIUS)
    if clicked_ctrl_i is not None:
      if len(self.knots) > 2:
        if clicked_ctrl_i % 3 == 0:
          knot_idx = math.floor((clicked_ctrl_i + 1) / 3)
          if knot_idx >= len(self.knots):
            knot_idx = 0
          self.knots.pop(knot_idx)
          self.__update_curve()
    else:
      pos = pygame.Vector2(tuple(self.vm.viewport_point_to_world(pos)))
      t = min(np.linspace(self.curve.start(0), self.curve.end(0), 100), key = lambda t: pos.distance_squared_to(self.curve(t)))
      
      knot = PathKnot(pos, self.curve.tangent(t))
      self.knots.insert(math.ceil(t), knot)
      self.__update_curve()

  def draw(self, surface):
    KNOT_COLOR = pygame.Color(100, 255, 100)
    HANDLE_COLOR = pygame.Color(100, 100, 255)

    if self.control_enabled:
      pygame.draw.lines(surface, 'white', False, self.vm.world_point_to_viewport(self.approx_pts))

    pygame.draw.line(surface, 'red', self.vm.world_point_to_viewport(self.left_wall[0]), self.vm.world_point_to_viewport(self.right_wall[0]), width = 5)
    pygame.draw.line(surface, 'red', self.vm.world_point_to_viewport(self.approx_pts[0]), self.vm.world_point_to_viewport(self.approx_pts[0] + self.curve.tangent(0)), width = 5)

    pygame.draw.lines(surface, 'blue', False, self.vm.world_point_to_viewport(self.left_wall))
    pygame.draw.lines(surface, 'yellow', False, self.vm.world_point_to_viewport(self.right_wall))

    if self.control_enabled:
      viewport_ctrl_pts = self.vm.world_point_to_viewport(self.ctrl_pts)
      for i, ctrl_pt in enumerate(viewport_ctrl_pts):
        is_knot = i % 3 == 0
        if is_knot:
          start = viewport_ctrl_pts[i - 1] if i > 0 else ctrl_pt
          end = viewport_ctrl_pts[i + 1] if i < len(viewport_ctrl_pts) - 1 else ctrl_pt
          pygame.draw.line(surface, HANDLE_COLOR, start, end, width = 2)
            
        pygame.draw.circle(surface, KNOT_COLOR if is_knot else HANDLE_COLOR, ctrl_pt, 5)

    if len(self.left_cones) > 0:
      for cone in self.vm.world_point_to_viewport(self.left_cones):
        pygame.draw.circle(surface, 'blue', cone, 3)
    
    if len(self.right_cones) > 0:
      for cone in self.vm.world_point_to_viewport(self.right_cones):
        pygame.draw.circle(surface, 'yellow', cone, 3)
