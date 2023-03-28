import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import os
from pandas import read_csv
from PIL import Image, ImageDraw, ImageFont
import random
import string
import sys
from typing import Tuple, List


######################################################
#               HELPER FUNCTIONS                     #
######################################################

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

def calc_percent_inside(coords: Tuple[List[float], List[float]], data_coords: Tuple[List[float], List[float]]) -> float:
    """Calculates the percentage of cells inside a coordinate list

    First converts the coordinates to a path and calculates % of cells inside.
    Used in debugging, to calculate the % of cells inside human drawn gate.
    
    Parameters
    ----------
    coords: Tuple[List[float], List[float]]
    The coordinates for the contour.
    
    data_coords: Tuple[List[float], List[float]]
    The coordinates for the dataset.

    Returns
    -------
    The percentage of cells inside the path. 
    Type: float.
    """
    
    path = _coord_to_path(coords)
    dataset_map = [(data_coords[0][i], data_coords[1][i]) for i in range(len(data_coords[0]))]
    c = path.contains_points(dataset_map)
    

    return (np.sum(c)/len(dataset_map))*100

def _coord_to_path(coords: Tuple[List[float], List[float]]) -> Path:
    """Converts the coordinates of a contour into a path object

    The path object is required to calculate the % of cells inside.

    Parameters
    ----------
    coords: Tuple[List[float], List[float]]
    The coordinates for the path: ([x1,x2,...], [y1,y2,...])
    
    
    Returns
    -------
    path : Path
    The path object describing the contour.
    """
    
    verts = []
    codes = []
    codes = [Path.LINETO] * len(coords[0])
    coords = np.asarray(coords)
    transpose = coords.T
    verts = list(zip(transpose[:, 0], transpose[:, 1]))
    codes[0] = Path.MOVETO
    codes[-1] = Path.CLOSEPOLY
    path = Path(verts, codes)
    return path

def _read_gate(gate_dataset_dir: str):
    """Reads the gate CSV returned from the GateVertexTool get function.
    
    Parameters
    ----------
    gate_dataset_dir : str
    The directory of the gate dataset.
    
    Returns
    -------
    coords: Tuple[List[float], List[float]]
    The coordinates of the gate.
    """
    
    gate = read_csv(gate_dataset_dir)  
    # Based on the way the get function returns from the GateVertexTool, the coordinates are in the name of the 7th column, preceded by a "b'".
    xy_coords = (gate.iloc[:,7].name[2:-1]).split(",")
    generator = pairwise(xy_coords)
    x_coords = []
    y_coords = []
        
    for elem in generator:
        x_coords.append(float(elem[0]))
        y_coords.append(float(elem[1]))
        
    # These next two lines are to close the gate
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    
    return (x_coords, y_coords)

def _read_dataset(dataset_dir, x_name='FITC-A-Compensated' , y_name='BSC-A'):
    """Reads the gate CSV returned from the GateVertexTool get function.
    
    Parameters
    ----------
    dataset_dir : str
    The directory of the dataset
    
    Returns
    -------
    coords: Tuple[List[float], List[float]]
    The coordinates of the the full dataset.
    """
    
    cluster = read_csv(dataset_dir, usecols=[x_name, y_name])
    x = cluster.iloc[:, :][x_name]
    y = cluster.iloc[:, :][y_name]
    return (x,y)

def plot_gate_and_dataset(gate_coords, data_coords, sample_name):
    """Plots the scatterplot as well as the gate overlayed.
    
    Parameters
    ----------
    gate_coords : Tuple[List[float], List[float]]
    Tuple of the gate coordinates ([x0,x1,...],[y0,y1,...])
    
    data_coords : Tuple[List[float], List[float]]
    Tuple of the dataset coordinates ([x0,x1,...],[y0,y1,...])
    
    sample_name : str
    The sample name of the dataset.
    
    Returns
    -------
    img : array
    Returns an image of the plot.
    """
    
    perc = round(calc_percent_inside(gate_coords, data_coords),3)
    fig = plt.figure(figsize=(10, 7))
    plt.scatter(data_coords[0],data_coords[1], s=1, c='#778899')
    plt.plot(gate_coords[0], gate_coords[1])
    plt.xscale("log")
    plt.xlim(10e1,10e5)
    plt.ylim(0,1e6)
    plt.xlabel("FITC-A-Compensated")
    plt.ylabel("BSC-A")
    plt.title(f"{sample_name}, {perc}%")
    return fig
    
def plot_figure(gate_dataset_dir, dataset_dir, sample_name):
    """Wrapper function to read all the CSVs and plot it.
    
    Parameters
    ----------
    gate_dataset_dir : str
    The directory of the gate coordinates.
    
    dataset_dir : str
    The directory of the full dataset.
    
    sample_name : str
    The sample name of the dataset.
    
    Returns
    -------
    fig : Matplotlib figure
    The figure of the plot.
    """
    
    gate_coords = _read_gate(gate_dataset_dir)
    data_coords = _read_dataset(dataset_dir)
    fig = plot_gate_and_dataset(gate_coords, data_coords, sample_name)
    return fig

def _generate_report_page(rootdir, width, height, offset, label_size, expt_title, plate):
    new_height = height * 8 + (offset * 7) + label_size + expt_title
    new_width = width * 12 + (offset * 11) + label_size
    new_im = Image.new('RGB', (new_width, new_height), color=(255,255,255,0))

    # Make the labels
    draw = ImageDraw.Draw(new_im)
    font = ImageFont.truetype("czfacsautomation/integration/Arial Bold.ttf", 84)
    title = ImageFont.truetype("czfacsautomation/integration/Arial Bold.ttf", 200)


    # Label the experiment name
    draw.text((new_width//2, expt_title//2),plate, (0,0,0), font=font)

    # Label the rows
    for row in ['A','B','C','D','E','F','G','H']:
        y_offset = label_size + expt_title + height // 2 +  (height) * (ord(row) - 65) + offset * (ord(row) - 65)
        draw.text((label_size/2, y_offset), row, (0,0,0), font=font)
        
    # Label the columns
    for x in range(1,13):
        x_offset = label_size + width // 2 +  (width) * (x-1) + offset * (x-1)
        draw.text((x_offset, label_size/2 + expt_title), str(x), (0,0,0), font=font)
    
    return new_im

def generate_report(rootdir):
    """Generates PDFs for all the plots generated. Saves in the experiment folder.

    Parameters
    ----------
    rootdir : str
    The absolute directory of the experiment folder.

    Returns
    -------
    None.
    """
    
    well_rows = ['A','B','C','D','E','F','G','H']
    well_cols = [1,2,3,4,5,6,7,8,9,10,11,12]
    height = 350
    width = 500
    offset = 20
    label_size = 300
    expt_title = 200
    wells = []
    for row in well_rows:
        for col in well_cols:
            well = row + str(col)
            wells.append(well)

    all_files = os.listdir(rootdir)
    offset = 20
    height = 350
    width = 500
    label_size = 300
    expt_title = 200
    new_height = height * 8 + (offset * 7) + label_size + expt_title
    new_width = width * 12 + (offset * 11) + label_size
    new_im = Image.new('RGB', (new_width, new_height), color=(255,255,255,0))

    # Make the labels
    draw = ImageDraw.Draw(new_im)
    font = ImageFont.truetype("czfacsautomation/integration/Arial Bold.ttf", 84)
    title = ImageFont.truetype("czfacsautomation/integration/Arial Bold.ttf", 200)

    # Label the experiment name
    draw.text((new_width//3, expt_title//3),rootdir, (0,0,0), font=font)

    # Label the rows
    for row in ['A','B','C','D','E','F','G','H']:
        y_offset = label_size + expt_title + height // 2 +  (height) * (ord(row) - 65) + offset * (ord(row) - 65)
        draw.text((label_size/2, y_offset), row, (0,0,0), font=font)
        
    # Label the columns
    for x in range(1,13):
        x_offset = label_size + width // 2 +  (width) * (x-1) + offset * (x-1)
        draw.text((x_offset, label_size/2 + expt_title), str(x), (0,0,0), font=font)

    pages = []
    plates = []

    for file in all_files:
        plate = file.split("-")[0]
        if plate not in plates:
            plates.append(plate)
            page = _generate_report_page(rootdir, width, height, offset, label_size, expt_title, plate)
            pages.append(page)

        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
                temp = []
                for file2 in os.listdir(d):
                    if "generated_plot" in file2:
                        d2 = os.path.join(d, file2)
                        img = Image.open(d2)
                        img.load()
                        img = img.resize((width,height))
                        data = np.asarray(img, dtype="int8")
                        sample_name = file2[:file2.find("_generated_plot")]
                        # There are sometimes 2 results, e.g., 'G12' will result in 'G1' and 'G12'. Choose the last sample
                        sample = [well for well in wells if well in sample_name][-1]
                        # Sample will e.g., be 'G1'. Use the numbers as the x_offset, and letters as the y_offset
                        x_offset = label_size + (int(sample[1:]) - 1) * offset + (int(sample[1:]) - 1) * width
                        y_offset = label_size + expt_title + (ord(sample[0]) - 65) * offset + (ord(sample[0]) - 65) * height
                        idx = plates.index(plate) #Find the index of the page to paste it on, which should be 1:1 with the plate it matches
                        pages[idx].paste(img, (x_offset,y_offset))
    for i in range(len(pages)):
        pages[i].save(f"{rootdir}/{plates[i]}_summary.pdf")

######################################################
#                 MAIN FUNCTION                      #
######################################################

def generate_images(rootdir, sample_wanted=[], generate_pdf=False):
    sample_files = []
    sample_names = []
    process_all = False
    if len(sample_wanted) == 0:
        process_all = True
    
    # First, do some sanity check on the samples_wanted (if doing a subset of samples)
    all_files = os.listdir(rootdir)
    if not process_all:
        for sample in sample_wanted:
            if sample not in all_files:
                print("==============ERROR==============")
                print(f"An invalid sample was entered: {sample}. Please check for correct sample name.")
                print("Correctly named samples will still be processed.")
                print("=================================")
    
    # After the sanity check, add the relevant files
    for file in all_files:
        if not process_all:
            if file not in sample_wanted:
                continue
                # Not a sample we want to process, skip to the next one
        
        d = os.path.join(rootdir, file)
            
        if os.path.isdir(d):
            temp = []
            for file2 in os.listdir(d):
                if ".png" not in file2 and ".DS_Store" not in file2:
                    d2 = os.path.join(d, file2)
                    temp.append(d2)
            sample_names.append(file)
            sample_files.append(temp)
    


    for i in range(len(sample_names)):
        print("=================================")
        print(f"Plotting {sample_names[i]}.")
        print("=================================")
        gate_dataset_idx = 0 if "gate.csv" in sample_files[i][0] else 1
        dataset_idx = int(not gate_dataset_idx)

        gate_dataset_dir = sample_files[i][gate_dataset_idx]
        dataset_dir = sample_files[i][dataset_idx]
        fig = plot_figure(gate_dataset_dir,dataset_dir, sample_names[i])
        d = os.path.join(rootdir, sample_names[i])
        # Check to see if a plot has already been generated
        already_exists = False
        for files in os.listdir(d):
            if '_generated_plot' in files:
                already_exists = True

        if not already_exists:
            # Generate a random string for a unique image name -- important for storing in places like Confluence!
            rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            img_filename = f"{d}/{sample_names[i]}_generated_plot_{rand}.png"
            fig.savefig(img_filename)


    print("=================================")
    print("Finished plotting images.")
    print("=================================")

    if generate_pdf:
        print("=================================")
        print("Generating summary report.")
        print("=================================")
        generate_report(rootdir)
        print("=================================")
        print("Finished generating summary report.")
        print("=================================")

def main():
    """Plots the exported data from an experiment in the Sony software
    """
    while True:
        print("=================================")
        print("Starting script to plot exported data!")
        print("=================================")
        rootdir = input("Paste in the directory of your folder here: ")
        samples_wanted = input("\nEnter the samples you want here in the following format: sample1,sample2,sample3\nIf you would like all samples, press enter:")
        generate_pdf = input("\nDo you want to generate a summary pdf? (y/n): ")
    
        if generate_pdf in ['y', 'Y']:
            generate_pdf = True
        else:
            generate_pdf = False
        print("\nWorking on your data...\n")
        try:
            generate_images(rootdir, samples_wanted, generate_pdf)
            break
        except Exception as e:
            print("=================================")
            print("There was a problem. Please fix and then proceed:")
            print(e)
            print("=================================")
    
    
if __name__ == '__main__':
        try:
            flag = str(sys.argv[1])
            if flag == '-h':
                print("=================================")
                print("HELP")
                print("=================================")
                print("This script will generate matplotlib plots for all or a subset of samples generated from the sort_scraper.py.")
                print("To run all samples, type in the command line: python3 plot_exported_data.py '[rootdir]'")
                print("e.g.: python3 plot_exported_data.py '/Users/emily.huynh/Downloads/20210915VTLibrarySort4'")
                print("To run a subset of samples, type in the command line: python plot_exported_data.py '[rootdir]' 'sample1,sample2,sample3'")
                print("Images will save in your original folder.")
                print("To generate a report, type in the command line: python plot_exported_data.py -r '[rootdir]' 'sample1,sample2,sample3'")
                print("=================================")
                sys.exit(2)
            main()    
        except IndexError as e:
            print("Index Error: ", e)
            print("python plot_exported_data.py -h")
            sys.exit(2)
        