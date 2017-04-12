"""Util interpolation and distance calculation methods for gps_mapper."""

import cv2
import math
import numpy as np
from collections import namedtuple


EARTH_RADIUS = 6371.0088 # radius of Earth in km


ImageInfo = namedtuple('ImageInfo', 'linewidth, height, width')
Sigmas = namedtuple('Sigmas', 'sigma_x, sigma_y')


def interpolate(current_point, next_point, sigmas, iminfo):
    """Connects a pair of points with a tangential curve and applies Gaussian blur.

    Arguments:
        current_point: starting point (i.e. location of the car)
        next_point: next waypoint
        line_width: width in pixels of line used to interpolate between points
        sigmas: namedtuple of (sigma_x, sigma_y) 
                    Gaussian parameters (higher => more blurry)
        height, width: dimensions of the output image in pixels
    """
    line_width, height, width = iminfo
    output = np.zeros((height, width), np.uint8)
    for i in range(len(points) - 1):
        pt1 = points[i]
        pt2 = points[i+1]
        cv2.line(output, pt1, pt2, [255, 255, 255], line_width)
    output = cv2.GaussianBlur(output, sigmas, 0)
    return output

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance between two lat-lon points in kilometers."""
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    delta_lat = (lat2 - lat1)
    delta_lon = (lon2 - lon1)
    angle = (math.sin(delta_lat / 2)**2
          + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon/2)**2)
    unit_distance = 2 * math.atan2(math.sqrt(angle), math.sqrt(1 - angle))
    return EARTH_RADIUS * unit_distance

def normalized_points(points, top_left, ll_height, ll_width, iminfo):
    """
    Takes a list of points (tuples of x, y coordinates) and an output image size
    and returns a transformed list of points that fit in the output image.
    """
    return [((x - top_left[0]) * iminfo.width / ll_width,
            (y - top_left[1]) * iminfo.height / ll_height)
            for (x, y) in points]

def normalize_single_point(point, top_left, ll_height, ll_width, iminfo):
    """Normalizes single point."""
    return ((point[0] - top_left[0]) * iminfo.width / ll_width,
            (point[1] - top_left[1]) * iminfo.height / ll_height)

def window(points, loc, angle, sigmas, iminfo):
    """Returns frame with the line of points that fit, given current location.

    Takes a list of points, a location, an angle in radians,
    and optionally a height and width in order to
    return the angled rectangular region of the image of the specified size,
    with the location specifying the bottom middle point of the image.
    The image itself is the blurred interpolation of all the points
    (we only construct the relevant portion of the rotated image).

    Arguments:
        points: list of (x, y) tuples representing points
        loc: tuple of (x, y) representing
                  the current car location to center the
                  bottom of the window at in pixels
        angle: angle in rad to rotate rectangular region by (counterclockwise)
        sigmas: (sigma_x, sigma_y) Gaussian kernel parameters
        iminfo: (line_width, height, width)
                    line width in pixels to interpolate between points
                    and dimensions of output image in pixels as a namedtuple
    """
    out = []
    parallel = (math.cos(angle), -math.sin(angle))
    perpendicular = (math.sin(angle), math.cos(angle))
    for (x, y) in points:
        x_img = (x * parallel[0] + y * parallel[1] + loc[0]
                 - loc[0] * parallel[0] - loc[1] * parallel[1])
        y_img = (x * perpendicular[0] + y * perpendicular[1] + loc[1]
                 - loc[0] * perpendicular[0] - loc[1] * perpendicular[1])
        # when adding the points back,
        # translate them to the proper location for the final image
        out.append((x_img + (iminfo.width/2 - loc[0]), y_img + (iminfo.height - loc[1])))
    return interpolate([(int(round(x)), int(round(y))) for (x, y) in out], 
                       sigmas, iminfo)

def dimensions(points):
    """Returns the width and height in kilometers given lat/long points."""
    x_vals = [x for (x, y) in points]
    y_vals = [y for (x, y) in points]
    top_left = (min(x_vals), max(y_vals))
    bottom_right = (max(x_vals), min(y_vals))
    x_range = haversine(top_left[0], top_left[1], bottom_right[0], top_left[1])
    y_range = haversine(top_left[0], top_left[1], top_left[0], bottom_right[1])
    return y_range, x_range

def corners(flipped_points):
    """
    Takes a set of lat-lon points that have been
    flipped to image array coordinates and finds
    the top left and and bottom right corner coordinates.
    """
    x_vals = [x for (x, y) in flipped_points]
    y_vals = [y for (x, y) in flipped_points]
    top_left = (min(x_vals), min(y_vals))
    bottom_right = (max(x_vals), max(y_vals))
    return top_left, bottom_right
