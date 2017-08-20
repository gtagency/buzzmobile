from math import pi, sin, cos, sqrt
import sys

EARTH_RADIUS = 6378137.0 # we're not using params because this is gzb specific
FLATTENING = 1.0/298.257223563
EXCENTRICITY2 = 2 * FLATTENING - (FLATTENING**2)

REF_LAT = 49.9
REF_LON = 8.9
REF_HEAD = 0.0
REF_ALT = 0.0

TEMP = 1.0 / (1.0 - EXCENTRICITY2 * sin(REF_LAT * pi/180.0) * sin(REF_LAT * pi/180.0))
PRIME_VERT_RADIUS = EARTH_RADIUS * sqrt(TEMP)
NORTH_RADIUS = PRIME_VERT_RADIUS * (1 - EXCENTRICITY2) * TEMP
EAST_RADIUS = PRIME_VERT_RADIUS * cos(REF_LAT * pi/180.0)

def convert(x, y):
    lat = REF_LAT + ((cos(REF_HEAD) * x + sin(REF_HEAD) * y) / NORTH_RADIUS) * 180.0/pi
    lon = REF_LON - ((-sin(REF_HEAD) * x + cos(REF_HEAD) * y) / EAST_RADIUS) * 180.0/pi
    return (lat, lon)

def main():
    print("[note] expecting arguments as: x y")
    x = float(sys.argv[1])
    y = float(sys.argv[2])
    (lat, lon) = convert(x, y)
    print("[out] {0} {1}".format(lat, lon))

if __name__=='__main__': main()
