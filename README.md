# ![bzm](/buzzmobile_small.png?raw=true) buzzmobile [![Build Status](https://circleci.com/gh/gtagency/buzzmobile/tree/master.svg?style=svg)](https://circleci.com/gh/gtagency/buzzmobile/tree/master)



An autonomous parade vehicle, modeled after Georgia Tech's Rambling Wreck

Architecture
------------

A list of available nodes and an overview of the architecture is available
[here](https://docs.google.com/drawings/d/1Lryui91lSutyC1TQhDmWI3JqDfefNB9E9RoSaBPHhcE/edit?usp=sharing).

![architecture](/architecture.png?raw=true)


Environment
-----------

To get started, be running Ubuntu 16.04 (required for ROS Kinetic) with python
2.7 installed. Then run:

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/gtagency/buzzmobile.git
cd buzzmobile
./install
```

If you already have ROS Kinetic installed, you can just clone directly into
`~/catkin/src/` and run the install script.
If you want to manually install ROS Kinetic you can follow the tutorial
[here](http://wiki.ros.org/kinetic/Installation/Ubuntu).

The install script will create a virtualenv, install system dependencies
(including ROS Kinetic), install python dependencies, build the package, and
source all required files. It will also put the `rosinit`, `rosdevel` and
`rosvenv` aliases in your `.bashrc`.

To use the google maps api, you'll need two api keys. Put one under
`buzzmobile/sense/maps_querier/googlemapskey.py` and one under
`buzzmobile/tools/route_mapper/googlemapskey.py` as shown below. Note that the
keys need to have proper permissions set in the [Google API
Console](https://console.developers.google.com/), for use of the Google Maps API
and the Google Maps Static API, respectively.

```python
googlemapskey='your_secret_api_key'
```

To use the gps and the lidar nodes, you will need user permissions to directly
access the usb ports for gps and lidar. For that, do:

```bash
sudo usermod -aG dialout <YOUR USERNAME>
```

You will then need to log in and out again. Simply starting a new terminal is
not sufficient. The Linux kernel will not refresh groups until the user
completely logs out and logs in again.


Running
-------

Make sure you are running inside the virtualenvironment, or things will
appear broken: `rosvenv`.

To start running, you must first run `catkin_make` from the `~/catkin_ws` dir.
If there aren't any issues with the build, you can run `roscore` to start the
main ROS process.

Create new tabs for every node and run them as such:

```bash
rosrun buzzmobile image_const.py
```

```bash
rosrun buzzmobile edge_detector
```

```bash
rosparam set usb_cam/pixel_format yuyv
rosrun usb_cam usb_cam_node
```

Note that rospy nodes don't require `catkin_make` to run, but do require the `.py`
extension. If you're writing a new rospy node, also make sure the file is made
executable, and has `#!/usr/bin/env python` as its first line.

```bash
chmod +x path/to/rospy_node.py  # make sure file has shebang
rosrun buzzmobile rospy_node.py
```

Some nodes require parameters that are defined in the
`buzzmobile/constants.yaml` file. To load those constants as `rosparam`s, do:

```bash
rosparam load ~/catkin_ws/src/buzzmobile/buzzmobile/constants.yaml
```

If you want to visualize your nodes, you can run the ROS visualizer (`rviz`),
`image_view`, or `rqt_gui`. These three have different ways of visualizing
messages being published:

```bash
rviz 
rosrun image_view image_view image:=some_imgmsg
rqt_gui 
```

To load the buzzmobile mission control, load `rqt_gui` with the mission control
perspective (configuration) file:

```bash
rosrun rqt_gui rqt_gui --perspective-file=buzzmobile/tools/mission_control/Default.perspective
```

To run the GPS node, do:

```bash
rosrun nmea_navsat_driver nmea_serial_driver _port:=/dev/ttyUSB0 _baud:=4800
```

To run the Lidar node, do:

```bash
rosrun hokuyo_node hokuyo_node port:=/dev/ttyACM0
```

Note that `/dev/ttyUSB0` and `/dev/ttyACM0` are the default serial ports for GPS
and Lidar respectively. These may or may not be different. Here are some useful
commands for debugging if things aren't set up correctly:

```bash
ls -l /dev/ttyACM0  # List permissions. Will output failure if /dev/ttyACM0 is not set.
sudo chmod a+rw /dev/ttyACM0  # Sets read/write permissions for all users, not recommended.
```

If you need to mock a polyline, this tool will be useful: [google polyline util](https://developers.google.com/maps/documentation/utilities/polylineutility)


Recording
---------

If you want to record the messages being outputted by certain nodes, you can use
rosbag:

```
mkdir ~/bagfiles
cd ~/bagfiles
rosbag record -O filename /message/name
```

To see info about the recorded data, do `rosbag info filename.bag`

To play the data (and publish those messages), do `rosbag play test.bag`. To play
in a loop, just add the `-l` flag.

Developing
----------

If you ever need to add ros dependencies, add them to `buzzmobile/packages.xml` and install them with:

```bash
cd ~/catkin_ws/src
rosdep install -y --from-paths ./buzzmobile/buzzmobile --ignore-src --rosdistro=kinetic
```

If you need to add python deps, make sure you're in the virtual environment (`rosvenv`), then add the dep to `buzzmobile/setup.py` and do:

```bash
cd ~/catkin_ws/src/buzzmobile
pip install -e buzzmobile
```

Alternatively, you can update both ros and python deps using:

```bash
./ci_scripts/update_deps
```


Starting Car
------------

To start car and prepare it for driving, perform the following steps:

1. Connect the battery
2. Flip the switch inside to turn the car on
3. Ensure all e-stops are disabled. (Red buttons on front and back in out position and enabled via remote)
4. Press the green button to start the motors (Car is now live)

The car starts in START mode where it receives no information. It must be switched
to MANUAL or AUTO for it to drive. See 'Manual Mode Controls' for details on
switching modes and operating the car.


Manual Mode Controls
--------------------

The `controller_node` node outputs a CarPose message and a CarState message
determined by input from a PS4 controller. To control these messages and operate
the car manually using the controller, use the following controls:

- Left Joystick: Change steering angle
- R2 (Right Trigger): Change velocity
- Square: Enable reverse. When this is held down, velocity is negated meaning the car will accelerate backwards.
- X: Honk the horn
- Home Button: Switch the car between AUTO and MANUAL modes.

The car starts in START mode. When pressed it will switch to MANUAL mode. Every
subsequent press toggles between AUTO and MANUAL mode.


Testing
-------

Testing is done with pytest. To run tests, you can run the script in
`ci_scripts/unittest`, which will run all unit tests. If you want to run a
specific test, make sure that the environment is initialized (run `rosvenv`,
`rosinit`, and `rosdevel`) then run:

```bash
cd ~/catkin_ws/src/buzzmobile/buzzmobile
pytest tests/unit/path/to/test.py
```

Be careful! Make sure not to run any tests from outside the inner `buzzmobile/`
dir, as that creates a name conflict in tests that try importing
`buzzmobile.std_msgs`.

Also make sure not to run tests from the root directory of the project, as there
is a virtualenv there: **running `pytest` will attempt to run thousands of
unittests included with the python interpreter.**

To write additional unit tests, please place within `buzzmobile/tests/unit` in
directories that match the source files, that is, tests for the
`buzzmobile/process/gps_mapper` node should go in
`buzzmobile/tests/unit/process/test_gps_mapper.py`. Integration and simulation 
tests should go in the `buzzmobile/tests/integration` and
`buzzmobile/tests/simulation` test subdirectories respectively.

In order to use the `test_util` api for writing tests, please refeer to the
readme in `buzzmobile/buzzmobile/tests/test_utils/`.
