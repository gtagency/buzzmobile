#!/usr/bin/env python
"""maps_querier: publishes polyline route from current location to destination.

Subscribes:
    /fix NavSatFix the current location
    destination String where we want to drive to
Publishes:
    polyline String encoded points of route from here to destination
"""

import googlemaps
import rospy

try:
    import googlemapskey as gmpskey
except ImportError as e:
    pass

from datetime import datetime
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import String


g = {} # globals
g['destination'] = None
g['published'] = False
g['fix'] = None
GMAPS = googlemaps.Client(key=gmpskey.googlemapskey)
pub = rospy.Publisher('polyline', String, queue_size=1)

def update_destination(new_destination):
    """Updates destination, and publishes polyline if possible."""
    g['destination'] = new_destination.data
    g['published'] = False
    if g['fix'] is not None:
        publish_polyline()

def update_fix(new_fix):
    """Updates current fix, and publishes polyline if possible."""
    g['fix'] = new_fix.latitude, new_fix.longitude
    if g['destination'] is not None and not g['published']:
        publish_polyline()

def publish_polyline():
    """Gets and publishes a polyline from current location to destination."""
    pub.publish(get_polyline(g['fix'], g['destination']))
    g['published'] = True

def get_polyline(start, destination):
    """Returns the polyline route from start to destination."""
    direction_result = get_directions(start, destination)
    return str(direction_result[0]['overview_polyline']['points'])

def get_directions(start, destination):
    """Returns a list of current driving directions from start to destination.
    start and destination may be strings or gps coordinates, e.g.,

    >>> get_directions("Atlanta, GA", "Seattle, WA")
    [direction object 1, direction object 2, ...]

    >>> get_directions((20.123, 41.382), (42.000, 3.142))
    [direction object 1, direction object 2, ...]
    """
    now = datetime.now()
    direction_result = GMAPS.directions(origin=start, destination=destination,
            alternatives=True, mode="driving", units="metric",
            departure_time=now)
    return direction_result

def maps_querier_node():
    """Initializes maps_querier node."""
    rospy.init_node('maps_querier')
    rospy.Subscriber('/fix', NavSatFix, update_fix)
    rospy.Subscriber('destination', String, update_destination)
    rospy.spin()

if __name__ == '__main__': maps_querier_node()
