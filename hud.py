import pygame
from abc import ABC

class CachedText:
  def __init__(self, defaultText, font, color):
    self.text = defaultText
    self.img = None
    self.font = font
    self.color = color

  def set_text(self, text):
    if text != self.text:
      self.text = text
      self.img = None

  def render(self):
    if self.img is None:
      self.img = self.font.render(self.text, True, self.color)

    return self.img


class CachedLabel(CachedText):
  def __init__(self, defaultText, font, color, position):
    super().__init__(defaultText, font, color)
    self.position = position

  def draw(self, screen: pygame.Surface):
    screen.blit(self.render(), self.position)


class HudView:
  def __init__(self):
    self.font = pygame.font.SysFont('arial.ttf', 24)

    self.lbl_blue_cone_count = CachedLabel('0', self.font, 'white', (20, 20))
    self.lbl_yellow_cone_count = CachedLabel('0', self.font, 'white', (20, 40))
    self.lbl_track_length = CachedLabel('0', self.font, 'white', (20, 60))
    self.lbl_hairpin_radius = CachedLabel('0', self.font, 'white', (20, 80))

    self.controls = [
      self.lbl_blue_cone_count,
      self.lbl_yellow_cone_count,
      self.lbl_track_length,
      self.lbl_hairpin_radius
    ]

    self.path_edit_enabled = True
    self.property_changed = {
      'blue_cones_count': lambda: self.lbl_blue_cone_count.set_text(f'Blue cones: {self.vm.blue_cones_count}'),
      'yellow_cones_count': lambda: self.lbl_yellow_cone_count.set_text(f'Yellow cones: {self.vm.yellow_cones_count}'),
      'track_length': lambda: self.lbl_track_length.set_text(f'Length: {self.vm.track_length:.2f}m'),
      'hairpin_radius': lambda: self.lbl_hairpin_radius.set_text(f'Hairpin radius: {self.vm.hairpin_radius:.2f}m'),
    }

  def bind(self, view_model):
    self.vm = view_model

  def draw(self, screen: pygame.Surface):
    for ctrl in self.controls:
      ctrl.draw(screen)

  def on_property_changed(self, name):
    f = self.property_changed.get(name, None)

    if f is not None:
      f()


class ViewNotifyProperty:
  def set_name(self, name):
    self.__name = name
    self.__field_name = f"__{name}"

  def __get__(self, obj, objtype=None):
    return getattr(obj, self.__field_name)

  def __set__(self, obj, value):
    defined = hasattr(obj, self.__field_name)
    if defined:
      old_value = getattr(obj, self.__field_name)

    if not defined or value != old_value:
      setattr(obj, self.__field_name, value)
      if obj.view is not None:
        obj.view.on_property_changed(self.__name)


def apply_view_notify_property(klass):
  for k, v in klass.__dict__.items():
    if isinstance(v, ViewNotifyProperty):
      v.set_name(k)
  return klass


@apply_view_notify_property
class HudViewModel:
  blue_cones_count = ViewNotifyProperty()
  yellow_cones_count = ViewNotifyProperty()
  track_length = ViewNotifyProperty()
  hairpin_radius = ViewNotifyProperty()

  def __init__(self):
    self.view = None

  def bind(self, view):
    self.view = view