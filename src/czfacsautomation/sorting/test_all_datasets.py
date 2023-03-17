# Profile the gate creation code to find bottlenecks
from datetime import datetime
from os import listdir, mkdir, path
import time
import traceback
import csv
import shutil

import matplotlib.pyplot as plt
from pandas import read_csv
import numpy as np
from pyinstrument import Profiler
from tqdm import tqdm

from create_gate import CreateGate


DISPLAY_TIME = 0.01
EXPORT_PREFIX = "temp"
EXPORT_GRAPH_DIR = (
    "./" + EXPORT_PREFIX + "_" + datetime.now().strftime("%d-%m-%Y %H-%M-%S") + "/"
)
DIR = "temp/"
SAVE = True
PREVIEW_ON = True
PROFILER_ON = False

if SAVE:
    mkdir(EXPORT_GRAPH_DIR)


def run(dataset, i, filename: str, csv_writer: csv.writer):
    """Used only for testing. Creates and saves the gate"""
    # print("==================")
    # print(f"Dataset: {i+1}")
    # print(dataset)
    # print("==================")
    cluster = read_csv(dataset, usecols=[x_name, y_name])

    if PROFILER_ON:
        profiler = Profiler()
        profiler.start()
    start = time.perf_counter()
    try:
        split_perc = 100
        split = int(100 / split_perc)

        x = cluster.iloc[::split, :][x_name]
        y = cluster.iloc[::split, :][y_name]
        c = CreateGate(
            x, y, f"{EXPORT_GRAPH_DIR}contourlines_{i}.png", save_contour=SAVE
        )
        cp, theight, tshape = c.create_gate()

        if PROFILER_ON:
            profiler.stop()
        stop = time.perf_counter()
        duration = stop - start

        if PROFILER_ON:
            print(profiler.output_text(unicode=True, color=True))  # for Mac
            # print(profiler.output_text()) # for TC Windows computer
        plt.figure(figsize=(10, 7))
        plt.scatter(c.x, c.y, s=1, c="#778899")
        plt.plot(c.gate_coords[0], c.gate_coords[1], "g")
        plt.plot(theight[0], theight[1])
        plt.plot(tshape[0], tshape[1])
        plt.xlabel(f"log( {x_name} )")
        plt.ylabel(y_name)
        plt.xlim([1, 7])
        # plt.ylim([0, 1e6])
        plt.title(
            f"Dataset: {i}, Custom Gate = {cp:.3f}%, {len(x)} cells, {duration:.1f}s"
        )
        filename = EXPORT_GRAPH_DIR + f"{i:03d}_{filename}.png"
        if SAVE:
            plt.savefig(filename)
        if PREVIEW_ON:
            plt.show(block=False)
            plt.pause(DISPLAY_TIME)
        plt.clf()

    except Exception as e:
        if PROFILER_ON:
            profiler.stop()
        print("==================ERROR==================")
        print(e)
        print(traceback.format_exc())
        # Display and save a blank graph
        plt.figure(figsize=(10, 7))
        plt.title(f"Dataset: {i+1} - ERROR")
        plt.scatter(c.x, c.y, s=1, c="#778899")
        plt.xlabel(f"log( {x_name} )")
        plt.ylabel(y_name)
        plt.xlim([1, 7])
        filename = EXPORT_GRAPH_DIR + f"{i:03d}_{filename}.png"
        if SAVE:
            plt.savefig(filename)

        if PREVIEW_ON:
            plt.show(block=False)
            plt.pause(DISPLAY_TIME)
        plt.clf()

        cp = "ERROR"
    finally:
        plt.close()
        if not csv_writer == None:
            csv_writer.writerow([i, cp])
        return filename, cp


dataset_folder = listdir(DIR)
length = len(dataset_folder)

if __name__ == "__main__":
    writer = None
    if SAVE:
        csv_filename = EXPORT_GRAPH_DIR + "cell_percs.csv"
        f = open(csv_filename, "a")
        writer = csv.writer(f)
        writer.writerow(["id", "cell_perc"])

    ### Running gating algorithm and generate plots
    cps = []
    filenames = []
    for i, file in enumerate(tqdm(sorted(dataset_folder[:]))):
        if i == 999:
            continue
        if ".csv" in file:
            dataset_name = DIR + file
            y_name = "BSC-A"
            x_name = "FITC-A-Compensated"
            filename, cp = run(
                dataset_name, i, file[: file.rfind(".")], csv_writer=writer
            )
            filenames.append(filename)
            cps.append(cp)

    if writer != None:
        f.close()

    ### Get and save outliers to separate directory
    mean = np.mean(cps)
    sd = np.std(cps)
    outliers_idx = np.argwhere(cps < mean - sd)
    outliers_idx = np.append(outliers_idx, np.argwhere(cps > mean + sd))

    filenames, cps = np.asarray(filenames), np.asarray(cps)
    outlier_filenames, outlier_percs = filenames[outliers_idx], cps[outliers_idx]

    if len(outlier_filenames) > 0 and SAVE:
        try:
            outlier_directory = path.dirname(filenames[0]) + "/outliers"
            mkdir(outlier_directory)
            [
                shutil.copy(
                    filename,
                    path.join(outlier_directory, path.basename(filename)),
                )
                for filename in outlier_filenames
            ]
        except Exception as e:
            print(f"Error saving outliers: {e}")
