import sys
import xml
import xml.etree.ElementTree as ET
from gzb_to_latlon import convert

def road_coordinates_to_latlons(road_coordinates):
    latlons = []
    for coordinate in road_coordinates:
        (lat, lon) = convert(coordinate[0], coordinate[1])
        latlons.append((lat, lon))
    return latlons

def world_xml_to_road_coordinates(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        if 'world' == str(child.tag):
            gui = xml.Element('gui')
            camera = xml.Element('camera')
            pose = xml.Element('pose')
            pose.text = '0 0 50 0 0 0'
            camera.append(pose)
            gui.append(camera)
            child.append(gui)


if __name__ == '__main__': world_xml_to_road_coordinates(sys.argv[1])
