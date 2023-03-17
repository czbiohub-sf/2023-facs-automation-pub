# Profile the gate creation code to find bottlenecks
import matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
from pyinstrument import Profiler
from skimage import measure, filters
from create_gate import CreateGate


dataset_name = 'user1_20190319automation_Sample Group - 1_SA6 profile.csv'
y_name = 'BSC-A'
x_name = 'FITC-A-Compensated'

cluster = read_csv(dataset_name, usecols=[x_name, y_name])
cluster[x_name] = np.log10(cluster[x_name])
# print(cluster.iloc[1:10])
# ax = plt.figure()
# plt.scatter(cluster[x_name], cluster[y_name], marker = '.')
# plt.xlabel(f'log( {x_name} )')
# plt.ylabel(y_name)
# plt.xlim([1, 6])
# plt.title(dataset_name)
# plt.show()
profiler = Profiler()
profiler.start()
# Convert scatter-plot to a histogram image
nbins = 100
hist, xedges, yedges = np.histogram2d(cluster[x_name], cluster[y_name], bins = nbins)
hist = filters.gaussian(hist.T/np.sum(hist), 3)
# contours = measure.find_contours(hist, 0.5*np.max(hist))

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
# ax.imshow(hist, origin='lower')
# for cn in contours:
#     ax.plot(cn[:, 1], cn[:, 0], linewidth=2)
xyticklocs = [i for i in range(0, 100, 10)]
xticklabels = [round(xedges[i], 1) for i in xyticklocs]
yticklabels = [round(yedges[i]) for i in xyticklocs]
# plt.xticks(xyticklocs, xticklabels)
# plt.yticks(xyticklocs, yticklabels)
# plt.show()

# ax = plt.figure()
xcenters = range(nbins) #[(xedges[i-1] + xedges[i])/2 for i in range(1, nbins+1)]
ycenters = range(nbins) #[(yedges[i-1] + yedges[i])/2 for i in range(1, nbins+1)]
X, Y = np.meshgrid(xcenters, ycenters)
# cs = ax.contour(X, Y, hist, origin='lower')
ax.set_aspect('equal')
plt.xticks(xyticklocs, xticklabels)
plt.yticks(xyticklocs, yticklabels)
plt.show()

profiler.stop()

print(profiler.output_text(unicode=True, color=True))
# print(c.update_gate_format())
# print(f'Number of coords: {len(c.gate_coords[0])}')

