from path_manager import PathManager
import csv
import random
import itertools
from dataclasses import dataclass
import numpy as np

@dataclass
class Cone:
  x: float
  y: float
  color: str

class ExportManager:
  def __init__(self, pm: PathManager):
    self.pm = pm

  def save(self):
    # Get all cones in a single list
    blue_cones = (Cone(x, y, 'blue') for (x, y) in self.pm.left_cones)
    yellow_cones = (Cone(x, y, 'yellow') for (x, y) in self.pm.right_cones)
    cones = list(itertools.chain(blue_cones, yellow_cones))

    # Randomize the cone list to remove track knowledge
    random.shuffle(cones)

    with open('cones.out.csv', 'w') as f:
      writer = csv.writer(f, lineterminator='\n')
      writer.writerow(('cone_x', 'cone_y', 'cone_color'))
      writer.writerows((cone.x, cone.y, cone.color) for cone in cones)

    centerline = list(self.pm.get_centerline())

    with open('centerline.out.csv', 'w') as f:
      writer = csv.writer(f, lineterminator='\n')
      writer.writerow(('centerline_x', 'centerline_y', 'left_boundary_dist', 'right_boundary_dist'))
      writer.writerows((pt[0], pt[1], self.pm.BOUNDARY_DISTANCE, self.pm.BOUNDARY_DISTANCE) for pt in centerline)