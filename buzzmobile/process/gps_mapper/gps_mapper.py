#!/usr/bin/env python
"""gps_mapper: node for creating gps_model, which defines immediate route.

Subscribes:
    /fix NavSatFix current coordinate location
    polyline String encoded coordinate points of route
    bearing Float64 direction the car is headed in radians (N is 0 rad)
Publishes:
    gps_model Image with immediate route to be taken
"""

import interpolate
import polyline as pl
import rospy

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64
from std_msgs.msg import String


g = {} # globals
g['bearing'] = None # Counter-clockwise angle from north in radians.
g['points'] = None # Polyline list of lat-lon points, after scaling to pixels.
g['location'] = None # Current location /fix
g['fixes'] = [] # list of coords last received, to minimize loss (median filter)
g['y_range'] = g['x_range'] = 0 # Dimensions of the path in km.
g['height'] = g['width'] = 0 # Scaled width of the points
g['ll_height'] = g['ll_width'] = 0 # lat-lon dimensions used to normalize points
g['top_left'] = (0, 0) # top left of image
g['bottom_right'] = (0, 0) # bottom righ of image
pub = rospy.Publisher('gps_model', Image, queue_size=1)
bridge = CvBridge()

X_SCALE = Y_SCALE = 1000 * rospy.get_param('pixels_per_m')
LINE_WIDTH = int(round(rospy.get_param('pixels_per_m')
                       * rospy.get_param('road_width')))
IMAGE_WIDTH = rospy.get_param('image_width')
IMAGE_HEIGHT = rospy.get_param('image_height')
IMINFO = interpolate.ImageInfo(LINE_WIDTH, IMAGE_HEIGHT, IMAGE_WIDTH)
MEDIAN_FILTER_SIZE = rospy.get_param('median_filter_size')
SIGMA_X = rospy.get_param('sigma_x')
SIGMA_Y = rospy.get_param('sigma_y')
SIGMAS = interpolate.Sigmas(SIGMA_X, SIGMA_Y)



def set_points(polyline):
    """Given a polyline as a ROS message, normalize and store the points."""
    if polyline is not None:
        points = pl.decode(polyline.data)
        # Calculate the y and x ranges (in kilometers).
        # This is because we must later flip the polyline points
        # (this is because a polyline point is a tuple of (lat, lon) while we
        # want (x, y) image coordinates), which
        # makes the y and x range calculations invalid later on.
        y_range, x_range = interpolate.dimensions(points)
        # Store y and x ranges.
        g['y_range'] = y_range
        g['x_range'] = x_range
        # Flip the points because we want the top of the image
        # to represent north.
        g['points'] = [(y, -x) for (x, y) in points]
        # Calculate top left and bottom right coordinates
        # after flipping the polyline points.
        top_left, bottom_right = interpolate.corners(g['points'])
        g['top_left'] = top_left
        g['bottom_right'] = bottom_right
        g['ll_height'] = abs(top_left[1] - bottom_right[1])
        g['ll_width'] = abs(top_left[0] - bottom_right[0])
        # Based on the accurate y and x ranges, calculate a height and width
        # that will scale our final image to our specified pixels_per_m
        # (pixels per meter) parameter.
        # Note that this is distinct from `image_height` and `image_width`,
        # which are the height and width of the current window that will be
        # passed to the frame merger!
        g['height'] = int(round(g['y_range'] * Y_SCALE))
        g['width'] = int(round(g['x_range'] * X_SCALE))
        # Store the normalized points.
        g['points'] = interpolate.normalized_points(g['points'], g['top_left'],
                      g['ll_height'], g['ll_width'], IMINFO)

def update_image():
    """
    Called every time the location of the car or the bearing of the car changes.
    Calculates the rotated point space and then interpolates the points in the
    specified window before publishing this updated window (image) to ROS.
    """
    if g['points'] is not None:
        # Normalize the current location to the coordinates of the
        # normalized polyline points.
        point = median_filter(g['location'])
        point = (point[1], -point[0])
        if g['y_range'] is not 0 and point is not None:
            point = interpolate.normalize_single_point(point, g['top_left'],
                    g['ll_height'], g['ll_width'], IMINFO)
            # Call method to calculate rotated points and interpolate a path
            # between the points that are in the current window
            # (based on the current location and bearing).
            result = interpolate.window(g['points'], point, g['bearing'],
                     SIGMAS, IMINFO)
            # Send the final image window as an image message through ROS.
            result_msg = bridge.cv2_to_imgmsg(result, encoding='mono8')
            pub.publish(result_msg)

def set_bearing(angle):
    """Given a radian bearing, update the current bearing and update image."""
    if angle is not None:
        g['bearing'] = angle.data
        if g['location'] is not None:
            update_image()

def set_location(fix_location):
    """Given a lat-lon, update current location and update image."""
    if fix_location is not None:
        g['location'] = (fix_location.latitude, fix_location.longitude)
        if g['bearing'] is not None:
            update_image()

def median_filter(fix):
    """Calculates new median coordinates, based on the ones saved."""
    if len(g['fixes']) > MEDIAN_FILTER_SIZE:
        g['fixes'].pop(0)
    g['fixes'].append(fix)
    sorted_points = sorted(g['fixes'])
    index = len(g['fixes']) // 2

    if len(g['fixes']) == 1:
        return sorted_points[0]
    elif len(g['fixes']) == 2:
        return ((sorted_points[0][0] + sorted_points[1][0]) * 0.5,
                (sorted_points[0][1] + sorted_points[1][1]) * 0.5)
    elif len(g['fixes']) % 2 and len(g['fixes']) > 1:
        return sorted_points[index]
    elif len(g['fixes']) > 1:
        return ((sorted_points[index][0] + sorted_points[index + 1][0]) * 0.5,
                (sorted_points[index][1] + sorted_points[index + 1][1]) * 0.5)
    else:
        return None

def gps_mapper_node():
    """Initializes gps_mapper node."""
    rospy.init_node('gps_mapper', anonymous=True)
    rospy.Subscriber('polyline', String, set_points)
    rospy.Subscriber('bearing', Float64, set_bearing)
    rospy.Subscriber('/fix', NavSatFix, set_location)
    rospy.spin()

if __name__ == '__main__': gps_mapper_node()
