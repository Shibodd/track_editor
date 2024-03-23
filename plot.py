import matplotlib.pyplot as plt
import csv
import numpy as np

with open("centerline.out.csv", "rt") as f:
  reader = csv.reader(f)
  assert(next(reader) == ['centerline_x', 'centerline_y', 'left_boundary_dist', 'right_boundary_dist'])

  pts = np.vstack([np.array([float(line[0]), float(line[1])]) for line in reader])

plt.plot(pts[:,0], pts[:,1])
plt.show()