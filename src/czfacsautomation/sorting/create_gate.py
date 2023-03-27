from json import load
import logging
from math import ceil
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path
import numpy as np
from pkg_resources import Requirement, resource_filename
from skimage import filters
from typing import List, Optional, Tuple


CONTOUR_SHAPE = 25  # the % of cells inside the contour selected for the gate shape
CONTOUR_HEIGHT = 80  # the % of cells inside the contour selected for the gate shape
TRANS_REMOVE_SHARP_CORNERS = (
    -50000
)  # amount to translate the contour mid line to remove sharp edges
GATE_WIDTH = 0.2  # the width of the gate created
NUM_BINS = 100  # the number of bins for the histogram
GAUSSIAN_STD = 5.5
MIN_CELL_PERCENTAGE = 0.1
TRANSLATE_RIGHT_OUTLIER_EXCLUSION_PERCENT = 0.02


class CreateGate:
    """Create a custom gate for a dataset

    :ivar dataset_length: The number of data points in the dataset
    :type dataset_length: int
    :ivar dataset_map: Map with x in logspace and negative x data removed. The map
                format is used to calculate percentage of cells inside an area using
                the path feature of mathplotlib
    :type dataset_map: List[Tuple[float, float]], i.e. [[x1, y1], [x2, y2],..]
    :ivar gate_coords: The custom gate drawn coordinates are stored here, this variable
                keeps getting modified with each step in the gate generation process
    :type gate_coords:Tuple[List[float], List[float]], i.e. [[x1, x2, ...], [y1, y2, ..]]
    :ivar save_contour_filename: Filename to save plot of contours. If None, does not save.
    :type save_contour_filename: str
    """

    def __init__(
        self,
        x: List[float],
        y: List[float],
        save_contour_filename: Optional[str] = None,
        save_contour: bool = True,
    ):
        """Initializes the instance variables

        :param x: x coordinates of the dataset
        :type x: List[float]
        :param y: y coordinates for the dataset
        :type y: List[float]
        :param save_kde: Name of directory where we should save the kernal density
                plot created, if None does not save the kde, defaults to None
        :type save_kde: str, optional
        """
        gui_config_file = resource_filename(
            Requirement.parse("czfacsautomation"), "config/gui_config.json"
        )
        with open(gui_config_file, "r") as f:
            self._gui_config = load(f)

        self.dataset_length = len(x)
        self.dataset_map, self.x = self._create_dataset_map(x, y)
        self.gate_coords = [[], []]
        self.save_contour_filename = save_contour_filename
        self.save_contour = save_contour
        self.desired_percent = self._gui_config["GATE_ENCLOSE_PERCENTAGE"][
            "percent"
        ]  # Maximum percent of cells in the gate

    def _create_dataset_map(
        self, x: List[float], y: List[float]
    ) -> Tuple[List[Tuple[float, float]], List[float]]:
        """Converts x to logspace and creates a map of dataset

        Removes datapoints where x is close to 0 or negative, as that throws
        an error when converting to log and creates anomalies in density plot
        (~about 10 out of 60k datapoints are excluded).

        :param x: x coordinates of the dataset
        :type x: List[float]
        :param y: y coordinates of the dataset
        :type y: List[float]
        :return: The dataset map i.e. [[x1, y1], [x2, y2],..] and list of x in logspace
        :rtype: Tuple[List[Tuple[float, float]], List[float]]
        """

        x_log = np.log10(x[x > 0]).tolist()
        self.y = y[x > 0].tolist()
        coords = np.array([x_log, y[x > 0]]).T

        return coords, x_log

    def filtered_contains_points(self, x_coords, y_coords):
        """Filters the points to check based on the min/max values of the polygon.

        The performance of matplotlib's `contains_points` function is sensitive to the number of points
        it needs to check. We can quickly filter out those points lying outside the rectangle defining the
        min/max limits of the gate, significantly reducing the points we send to `contains_points`
        and speeding up computation.

        :param x_coords: List of x-points of the polygon
        :type x_coords: list/np array
        :param y_coords: List of y-points of the polygon
        :type x_coords: list/np array
        :return: Numpy array containing the list of points within the min/max x/y bounds
        :rtype: List[float]
        """
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        x_mask = (self.dataset_map[:, 0] > x_min) & (self.dataset_map[:, 0] < x_max)
        y_mask = (self.dataset_map[:, 1] > y_min) & (self.dataset_map[:, 1] < y_max)
        mask = x_mask & y_mask
        return self.dataset_map[mask]

    def update_gate_format(self) -> str:
        """Creates a string to pass to the GateVertexTool to set gate
        The x coordinates are converted back from logspace, the last data point
        is removed, as it was only used to close the shape and the a
        comma separated string is created of the gate coordinates. This method
        is called last after create_gate() is called.
        :return: The string to pass to the GateVertexTool, 'x1,y1,x2,y2,....'
        :rtype: str
        """
        print(self.gate_coords[0])
        print(self.gate_coords[1])
        self.gate_coords[0] = self.gate_coords[0][:-1]
        self.gate_coords[1] = self.gate_coords[1][:-1]

        x_10pow = [10**i for i in self.gate_coords[0]]
        gate_vertex_input = ""
        comma = ""
        for x, y in zip(x_10pow, self.gate_coords[1]):
            gate_vertex_input = gate_vertex_input + "{}{},{}".format(comma, x, y)
            comma = ","
        return gate_vertex_input

    def create_gate(
        self,
    ) -> Tuple[float, Tuple[List[float], List[float]], Tuple[List[float], List[float]]]:
        """Creates gate by calling all the intermediate methods and stores it in gate_coords ivar.

        Parameters to tweak:

        :return: A tuple containing 1. The percentage of cells in the gate,
                2. The coordinates for the 50% contour line ([x1,x2,..], [y1,y2,..]),
                3. The coordinates for the 25% contour line ([x1,x2,..], [y1,y2,..]),
                2. and 3. are used in debugging, to plot the the contour lines with the gate
                and the scatter plot (see parse_data.py in the tests directory)
        :rtype: Tuple[float, Tuple[List[float], List[float]], Tuple[List[float], List[float]]]
        """
        cs = self._create_contour()
        contour50 = self._get_contour_percent(cs, CONTOUR_HEIGHT)
        contour25 = self._get_contour_percent(cs, CONTOUR_SHAPE)
        self.gate_coords = contour25
        height_req = max(contour50[1]) - min(contour50[1])
        self._extract_right_half(TRANS_REMOVE_SHARP_CORNERS)
        self._create_gate_shape(height_req, max(contour50[1]))
        self._create_closed_path(GATE_WIDTH)

        return self._translate_till_desired(), contour50, contour25

    def _create_contour(self) -> List[LineCollection]:
        """Creates a density contour plot on the dataset returns the collection of contours

        :return: The list of the density contour lines
        :rtype: List[LineCollection]
        """

        # Generate a 2d histogram, preprocess with a Gaussian filter to generate smoother contours
        hist, xedges, yedges = np.histogram2d(self.x, self.y, bins=NUM_BINS)
        hist = filters.gaussian(hist / np.sum(hist), GAUSSIAN_STD)
        xranges = range(NUM_BINS)
        yranges = range(NUM_BINS)
        X, Y = np.meshgrid(xranges, yranges)
        cs = plt.contour(
            hist.transpose(),
            levels=15,
            extent=[xedges.min(), xedges.max(), yedges.min(), yedges.max()],
        ).collections
        plt.close()

        if self.save_contour_filename and self.save_contour:
            plt.figure(figsize=(10, 7))
            try:  # save plot if directory given
                plt.clf()
                y_name = "BSC-A"
                x_name = "FITC-A-Compensated"
                plt.scatter(self.x, self.y, s=0.5, c="#778899")

                # Plot closed, circular contour lines
                for contour in cs:
                    path = contour.get_paths()

                    if len(path) == 0:
                        continue

                    path_x = path[0].vertices[:, 0]
                    path_y = path[0].vertices[:, 1]
                    path_arr = list(path[0].iter_segments())

                    # Ensure path is closed
                    if (
                        path_x[0] == path_x[-1]
                        and path_y[0] == path_y[-1]
                        and len(path_arr) > 3
                    ):
                        # Ensure path is not a vertical or horizontal line
                        if (not np.all(path_x == path_x[0])) and (
                            not np.all(path_y == path_y[0])
                        ):
                            x = contour.get_segments()[0][:, 0]
                            y = contour.get_segments()[0][:, 1]
                            plt.plot(x, y, "C0")

                plt.xlabel(f"log( {x_name} )")
                plt.ylabel(y_name)
                plt.xlim([1, 7])
                plt.title(f"{self.save_contour_filename}")
                plt.savefig(self.save_contour_filename)
            except Exception as e:
                print(e)
                print(f"Error trying to save KDE plot to {self.save_contour_filename}")

        return cs

    def _get_contour_percent(
        self, cs: List[LineCollection], percent: float
    ) -> Tuple[List[float], List[float]]:
        """Gets the contour line containing the desired % cells inside

        :param cs: The list of density plots generated by kde package
        :type cs: List[LineCollection]
        :param percent: The desired % of cells inside the density plot
        :type percent: float
        :return: The coordinates of the density plot with desired percentage
                [[x1, x2, ...], [y1, y2, ..]]
        :rtype: Tuple[List[float], List[float]]
        """

        cell_percentage = 100
        i = 0
        points = np.array([self.x, self.y])
        while cell_percentage > percent + 2:  # little over the desired %
            path = cs[i].get_paths()
            if len(path) == 0:
                i = i + 1
                continue
            path_x = path[0].vertices[:, 0]
            path_y = path[0].vertices[:, 1]
            path_arr = list(path[0].iter_segments())

            # Ensure path is closed
            if (
                path_x[0] == path_x[-1]
                and path_y[0] == path_y[-1]
                and len(path_arr) > 3
            ):
                # Ensure path is not a vertical or horizontal line
                if (not np.all(path_x == path_x[0])) and (
                    not np.all(path_y == path_y[0])
                ):
                    contains_array = path[0].contains_points(points.T)
                    cell_percentage = (
                        np.sum(contains_array) / len(self.dataset_map)
                    ) * 100
            i = i + 1

        x = cs[i - 1].get_segments()[0][:, 0]
        y = cs[i - 1].get_segments()[0][:, 1]
        gate_coords = [[], []]
        gate_coords[0] = list(x)
        gate_coords[1] = list(y)

        return gate_coords

    def _extract_right_half(self, shift_val: int = 0):
        """Extracts the shape of the right half of the contour line

        The contour line is an oval tilted to the right, to extract the right half
        first find the line that goes through the min and max y values in the
        increasing x to remove sharp corners due to contour lines with high convexity
        contour, and extract points below the line. The line can be translated along

        :param shift_val: How much to translate along x (more negative is more towards
                        increasing x), defaults to 0
        :type shift_val: int, optional
        """

        shift_val = 0
        x = self.gate_coords[0]
        y = self.gate_coords[1]
        mx_y, min_y = max(y), min(y)
        x_mxy, x_miny = x[y.index(mx_y)], x[y.index(min_y)]

        # Ensure min and max y values don't occur at the same x
        if x_mxy == x_miny:
            x_miny = x_miny - x_miny / 100
            x_mxy = x_mxy + x_mxy / 100

        m = (mx_y - min_y) / (x_mxy - x_miny)  # line gradient

        # Ensure that origin of the contour is on the left side
        # This is important because we want the path to terminate such that
        # it forms a backwards C (i.e we want the left-side to be "open")
        # Normally the contour origin is already on the bottom-left, but
        # there has been one errant dataset where the contour origin started on the bottom-right
        idx_x_min = np.where(x == np.min(x))[0][0]
        idx_x_min = len(x) - idx_x_min
        x = np.roll(x, idx_x_min)
        y = np.roll(y, idx_x_min)

        # Ensure slope is positive
        m = abs(m)

        c = mx_y - m * x_mxy  # line y intercept
        c = c + shift_val  # translate line along x

        x_final = []
        y_final = []

        for xp, yp in zip(x, y):
            if yp < (m * xp + c):  # extract points below the line
                x_final.append(xp)
                y_final.append(yp)
        while x_final[0] == x_final[-1]:
            x_final.pop()
            y_final.pop()
        self.gate_coords = [x_final, y_final]

    def _create_gate_shape(self, height_req: float, contour_maxy: float):
        """Creates the shape of the gate by scaling the current contour line

        To scale the contour line is first vertically translated to make the center
        the origin, then a scaling factor is applied, finally the line is shifted back
        to original center position.

        :param height_req: The desired height of the contour line
        :type height_req: float
        :param contour_maxy: The y value of the contour line before scaling
        :type contour_maxy: float
        """

        y_bf = self.gate_coords[1]
        mx_y, min_y = max(y_bf), min(y_bf)
        mid_y = (mx_y + min_y) / 2
        y_mid_origin = [i - mid_y for i in y_bf]  # make the mid the origin

        k = height_req / (max(y_mid_origin) - min(y_mid_origin))  # scaling factor
        logging.info("The scaling factor used to stretch gate: {}".format(k))
        y_stretched = [
            k * i for i in y_mid_origin
        ]  # apply scaling to translated contour line

        new_max = max(y_stretched) + mid_y
        diff = (
            contour_maxy - new_max
        )  # the effect of scaling on the required translation

        self.gate_coords[1] = (np.asarray(y_stretched) + mid_y + diff).tolist()

    def _create_closed_path(self, thickness: float):
        """Repeats the contour line a thickness away to create closed gate

        The GateVertexTool has a maximum number of coordinates (64) that it allows.
        To maintain that every other <step_size> point is skipped. The step_size is
        calculated to make sure the total points are less than 60

        :param thickness: The width of the gate
        :type thickness: float
        """

        # Get the height and midpoint prior to doing the 20/80 quantile cut
        prev_mx, prev_min = max(self.gate_coords[1]), min(self.gate_coords[1])
        prev_mid = (prev_mx + prev_min) / 2
        prev_height = prev_mx - prev_min

        q20, q80 = np.quantile(self.gate_coords[1], [0.2, 0.8], interpolation="nearest")
        idx20 = np.where(self.gate_coords[1] == q20)[0][0]
        idx80 = np.where(self.gate_coords[1] == q80)[0][0]
        self.gate_coords[0] = self.gate_coords[0][idx20:idx80]
        self.gate_coords[1] = self.gate_coords[1][idx20:idx80]

        # Scale the sliced gate to the pre-slice height
        new_mx, new_min = max(self.gate_coords[1]), min(self.gate_coords[1])
        new_height = new_mx - new_min
        height_scale_factor = prev_height / new_height
        self.gate_coords[1] = [i * height_scale_factor for i in self.gate_coords[1]]

        # Do a vertical translation using the difference of midpoints
        new_mx, new_min = max(self.gate_coords[1]), min(self.gate_coords[1])
        new_mid = (new_mx + new_min) / 2
        diff = new_mid - prev_mid
        self.gate_coords[1] = [i - diff for i in self.gate_coords[1]]

        points = len(self.gate_coords[0])
        step = ceil(2 * points / 60)  # Ensure total number of points < 60
        self.gate_coords[0] = [self.gate_coords[0][i] for i in range(0, points, step)]
        self.gate_coords[1] = [self.gate_coords[1][i] for i in range(0, points, step)]
        x_translate = [i + thickness for i in self.gate_coords[0]]
        y_translate = self.gate_coords[1].copy()
        x_translate.reverse()  # Add the repeated coords in reverse to create clockwise path
        y_translate.reverse()

        for i in range(len(x_translate)):
            self.gate_coords[0].append(x_translate[i])
            self.gate_coords[1].append(y_translate[i])

        self.gate_coords[0].append(self.gate_coords[0][0])  # to close the contour
        self.gate_coords[1].append(self.gate_coords[1][0])

    def _translate_till_desired(self) -> float:
        """Translates the gate along increasing x till "desired_percent" count is reached inside gate

        Some datasets have two clusters and there maybe a "desired_percent" count in between
        the two clusters. To avoid that, the gate is translated right in x using a large
        step size till 0% cell count is reached. Then the gate is translated left in x
        to the closest step that gives a count over the "desired_percent".

        :return: The percentage of cells after all the translations
        :rtype: float
        """

        small_step = 0.0025
        self._translate_x_right()
        self._rotateAndGetEnclosed()
        self._widen_left(self.desired_percent, small_step)

        contains_array = self._coord_to_path([self.gate_coords[0], self.gate_coords[1]])
        contains_array = contains_array.contains_points(self.dataset_map)
        cell_percentage = (np.sum(contains_array) / self.dataset_length) * 100.0

        return cell_percentage

    def _widen_left(self, exp_percent: float, step_size: float) -> List[float]:
        cell_percentage = 0
        right_edge = self.gate_coords[0][len(self.gate_coords[0]) // 2 : -1]
        left_edge = [x - GATE_WIDTH for x in right_edge]
        thickness = 0.1
        steps_percent = []

        # The "min_x_dist_before_check" is used to check that the gate has at least moved
        # a little bit before we begin to check for any blank regions to the left of the gate.
        # I.e, before we check for if there is only a small change in cell-percentage enclosed
        # per step, we want to ensure that the gate has moved a bit
        min_x_dist_before_check = (
            0.75  # chosen somewhat arbitrarily based on observation
        )
        min_steps = min_x_dist_before_check / step_size
        plateau_window_size = 50
        plateau = False
        tol = 1e-4
        num_steps = 0

        while cell_percentage < exp_percent and (
            plateau == False or cell_percentage < MIN_CELL_PERCENTAGE
        ):
            left_edge_shifted_left = [x - thickness for x in left_edge]
            y_coords = self.gate_coords[1]
            x_coords = np.concatenate((left_edge_shifted_left[::-1], right_edge))
            x_coords = np.append(x_coords, x_coords[0])
            contains_array = self._coord_to_path([x_coords, y_coords])
            points_to_check = self.filtered_contains_points(x_coords, y_coords)
            contains_array = contains_array.contains_points(points_to_check)
            cell_percentage = (np.sum(contains_array) / self.dataset_length) * 100.0
            steps_percent.append(cell_percentage)
            thickness += step_size

            if num_steps > min_steps:
                diffs = np.diff(steps_percent[-plateau_window_size:])
                mean_diffs = np.mean(diffs)
                plateau = mean_diffs < tol
            num_steps += 1

        self.gate_coords[0] = x_coords

        return steps_percent

    def _rotateAndGetEnclosed(self):
        rotation_angles = np.linspace(-0.1, 0, 10)
        gate_coords = np.array(
            [
                self.gate_coords[0] / np.max(self.gate_coords[0]),
                self.gate_coords[1] / np.max(self.gate_coords[1]),
            ]
        ).T
        min_cell_perc = 100
        opt_gate = []
        points_to_check = self.filtered_contains_points(
            gate_coords[:, 0], gate_coords[:, 1]
        )
        for angle in rotation_angles:
            rotated_gate = self._rotateAboutCenter(gate_coords.copy(), angle)
            contains_array = self._coord_to_path(
                [
                    rotated_gate[:, 0] * np.max(self.gate_coords[0]),
                    rotated_gate[:, 1] * np.max(self.gate_coords[1]),
                ]
            )
            contains_array = contains_array.contains_points(points_to_check)
            cell_percentage = (np.sum(contains_array) / self.dataset_length) * 100.0
            if cell_percentage < min_cell_perc:
                min_cell_perc = cell_percentage
                rotated_gate[:, 0] = rotated_gate[:, 0] * np.max(self.gate_coords[0])
                rotated_gate[:, 1] = rotated_gate[:, 1] * np.max(self.gate_coords[1])
                opt_gate = rotated_gate.copy()

        self.gate_coords[0] = opt_gate[:, 0]
        self.gate_coords[1] = opt_gate[:, 1]

    def _getRotationMatrix(self, theta):
        c, s = np.cos(theta), np.sin(theta)
        return np.array(((c, -s), (s, c)))

    def _translatePoints(self, points, x_translate, y_translate):
        points[:, 0] -= x_translate
        points[:, 1] -= y_translate

        return points

    def _rotatePoints(self, points, rotation_matrix):
        return np.dot(points, rotation_matrix.T)

    def _rotateAboutCenter(self, points, theta):
        points = np.asarray(points)
        x_vals = points[:, 0]
        y_vals = points[:, 1]
        xc = (np.max(x_vals) + np.min(x_vals)) / 2
        yc = (np.max(y_vals) + np.min(y_vals)) / 2
        points = self._translatePoints(points, xc, yc)
        rotation_matrix = self._getRotationMatrix(theta)
        rotated_points = self._rotatePoints(points, rotation_matrix)
        rotated_points = self._translatePoints(rotated_points, -xc, -yc)

        return rotated_points

    def _translate_x_right(self):
        """Translates gate to the maximum x-position of the distribution."""

        x_translate = np.asarray(self.gate_coords[0])
        x_diff = np.percentile(
            self.dataset_map[:, 0], (100 - TRANSLATE_RIGHT_OUTLIER_EXCLUSION_PERCENT)
        ) - np.max(x_translate)

        x_translate = x_translate + x_diff + GATE_WIDTH
        x_translate = x_translate.tolist()

        self.gate_coords[0] = x_translate

    def _translate_x_left(self, exp_percent: float, step_size: float) -> List[float]:
        """Translates gate towards negative x

        :param exp_percent: The desired % of cells inside the gate
        :type exp_percent: float
        :param step_size: The size of the increment for each translation
        :type step_size: float
        :return: List containing the % of cells inside at each increment
        :rtype: List[float]
        """

        cell_percentage = 0
        x_translate = np.asarray(self.gate_coords[0])
        steps_percent = []
        while cell_percentage < exp_percent:
            x_translate = x_translate - step_size
            contains_array = self._coord_to_path([x_translate, self.gate_coords[1]])
            contains_array = contains_array.contains_points(self.dataset_map)
            cell_percentage = (np.sum(contains_array) / self.dataset_length) * 100.0
            steps_percent.append(cell_percentage)

        # Pick closer of last and previous step
        if len(steps_percent) > 1:
            if np.abs(self.desired_percent - steps_percent[-2]) < np.abs(
                self.desired_percent - steps_percent[-1]
            ):
                x_translate += step_size
                steps_percent = steps_percent[:-1]

        x_translate = x_translate.tolist()
        self.gate_coords[0] = x_translate

        return steps_percent

    def _closest(self, lst: List[float], K: float) -> float:
        """Returns the value closest to K in a list

        :param lst: The list to parse through
        :type lst: List[float]
        :param K: Comparator used to select return value
        :type K: float
        :return: Value closest to K
        :rtype: float
        """

        return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]

    def _path_to_coord(self, path: Path) -> Tuple[List[float], List[float]]:
        """Takes a path object and returns a coordinate list

        :param path: The path object describing a closed contour
        :type path: Path
        :return: The coordinates for the path: ([x1,x2,..], [y1,y2,..])
        :rtype: Tuple[List[float], List[float]]
        """
        gate_coords = [[], []]
        for vv in path.cleaned().iter_segments():
            xy = vv[0]
            gate_coords[0].append(xy[0])
            gate_coords[1].append(xy[1])

        return gate_coords

    def calc_percent_inside(self, coords: Tuple[List[float], List[float]]) -> float:
        """Calculates the percentage of cells inside a coordinate list

        First converts the coordinates to a path and calculates % of cells inside.
        Used in debugging, to calculate the % of cells inside human drawn gate.

        :param coords: The coordinates for the contour
        :type coords: Tuple[List[float], List[float]]
        :return: The percentage of cells inside the path
        :rtype: float
        """

        path = self._coord_to_path(coords)
        c = path.contains_points(self.dataset_map)

        return (np.sum(c) / len(self.dataset_map)) * 100

    def _coord_to_path(self, coords: Tuple[List[float], List[float]]) -> Path:
        """Converts the coordinates of a contour into a path object

        The path object is required to calculate the % of cells inside.

        :param coords: The coordinates for the path: ([x1,x2,..], [y1,y2,..])
        :type coords: Tuple[List[float], List[float]]
        :return: The path object describing the contour
        :rtype: Path
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
