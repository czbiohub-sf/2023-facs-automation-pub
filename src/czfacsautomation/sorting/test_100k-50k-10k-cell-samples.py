# Profile the gate creation code to find bottlenecks
from datetime import datetime
import matplotlib.pyplot as plt
from os import listdir, mkdir
from pandas import read_csv
from pyinstrument import Profiler
from create_gate import CreateGate


DISPLAY_TIME = 1.0
EXPORT_GRAPH_DIR = "./" + datetime.now().strftime("%d-%m-%Y %H-%M-%S") + "/"
DIR = "validationSets/"
SAVE = False

if SAVE:
    mkdir(EXPORT_GRAPH_DIR)

def run(dataset, nm, i):
    """Used only for testing. Creates and saves the gate"""
    print("==================")
    print(f"Dataset: {i+1}")
    print(dataset)
    print("==================")
    cluster = read_csv(dataset, usecols=[x_name, y_name])

    x100 = cluster.iloc[::1, :][x_name]
    y100 = cluster.iloc[::1, :][y_name]
    x50 = cluster.iloc[::2, :][x_name]
    y50 = cluster.iloc[::2, :][y_name]
    x10 = cluster.iloc[::10, :][x_name]
    y10 = cluster.iloc[::10, :][y_name]

    gate100 = CreateGate(x100, y100)
    gate50 = CreateGate(x50, y50)
    gate10 = CreateGate(x10, y10)
    g100, _, _ = gate100.create_gate()
    g50, _, _ = gate50.create_gate()
    g10, _, _ = gate10.create_gate()
    plt.figure(figsize=(10, 7))
    plt.scatter(gate100.x, gate100.y, s=1, c='#778899')
    plt.plot(gate100.gate_coords[0], gate100.gate_coords[1], 'g', label='100%', alpha=0.5)
    plt.plot(gate50.gate_coords[0], gate50.gate_coords[1], 'b', label='50%', alpha=0.5)
    plt.plot(gate10.gate_coords[0], gate10.gate_coords[1], 'r', label='10%', alpha=0.5)
    plt.title(f"Dataset: {i+1}, 100 - {g100:.3f}%, 50 - {g50:.3f}%, 10 - {g10:.3f}%")
    plt.xlabel(f'log( {x_name} )')
    plt.ylabel(y_name)
    plt.xlim([1, 6])
    plt.legend()
    if SAVE:
        plt.show(block=False)
    else:
        plt.show(block=True)
    if SAVE:
        plt.savefig(EXPORT_GRAPH_DIR+f"{i+1}")

    print("\n\n==================")

dataset_folder = listdir(DIR)
length = len(dataset_folder)

if __name__ == "__main__":
    for i, file in enumerate(dataset_folder):
        if i == 100:
            continue
        if ".csv" in file:
            dataset_name = DIR + file 
            y_name = 'BSC-A'
            x_name = 'FITC-A-Compensated'
            run(dataset_name, 'dataset_plot', i)
