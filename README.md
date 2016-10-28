# buzzmobile [![Build Status](https://circleci.com/gh/gtagency/buzzmobile/tree/master.svg?style=svg)](https://circleci.com/gh/gtagency/buzzmobile/tree/master)
An autonomous parade vehicle

Architecture
------------

A list of available nodes and an overview of the architecture is available [here](https://docs.google.com/drawings/d/1Lryui91lSutyC1TQhDmWI3JqDfefNB9E9RoSaBPHhcE/edit?usp=sharing).

![architecture](/architecture.png?raw=true)

Environment
-----------

To get started, be running Ubuntu 14.04 (required for ROS Indigo).
Install ROS Indigo by following the tutorial [here](http://wiki.ros.org/indigo/Installation/Ubuntu).

It's a good idea to set up some helpful aliases in your `.bashrc`:

```bash
alias rosinit='source /opt/ros/indigo/setup.bash'
alias rosdevel='source ~/catkin_ws/devel/setup.bash' # needed for autocompletion

rosinit     # put these in your .bashrc too so they run everytime
rosdevel    # you open a new terminal window/tab.
```

We recommend using OpenCV 3. You can install it with:

```bash
sudo apt-get install ros-indigo-opencv3
```

To set up this repo, do:

```bash
cd ~
mkdir -p catkin_ws/src
cd catkin_ws/src
catkin_init_workspace
```

Now you can clone this repo into `~/catkin_ws/src` and run `rosdep install buzzmobile` to install some dependencies, like [usb_cam] and [nmea_navsat_driver].

To use the google maps api, you'll need two api keys. Put one under `buzzmobile/sense/maps_querier/googlemapskey.py` and one under `buzzmobile/tools/route_mapper/googlemapskey.py` as shown below. Note that the keys need to have proper permissions set in the [Google API Console](https://console.developers.google.com/), for use of the Google Maps API and the Google Maps Static API, respectively.

```python
googlemapskey='your_secret_api_key'
```

To use the gps and the lidar nodes, you will need user permissions to directly access the usb ports for gps and lidar. For that, do:

```bash
sudo usermod -aG dialout <YOUR USERNAME>
```
You will then need to log in and out again. Simply starting a new terminal is not sufficient. The Linux kernel will not refresh groups until the user completely logs out and logs in again.

To use a PS4 controller you will need to install the PS4 controller driver for Linux. For that, do:

```bash
sudo pip install ds4drv
```

Running
-------

To start running, you must first run `catkin_make` from the `~/catkin_ws` dir.
If there aren't any issues with the build, you can run `roscore` to start the
main ROS process.

Create new tabs for every node and run them as such:

```rosrun buzzmobile image_const```

```rosrun buzzmobile edge_detector```

```rosparam set usb_cam/pixel_format yuyv
rosrun usb_cam usb_cam_node```

Note that rospy nodes don't require `catkin_make`, but do require that the file be made executable, and the `.py` extension:

```bash
chmod +x path/to/rospy_node.py  # also make sure the file has the correct python shebang
rosrun buzzmobile rospy_node.py
```

Some nodes require parameters that are defined in the `buzzmobile/constants.yaml` file. To load those constants as `rosparam`s, do:

```bash
rosparam load buzzmobile/buzzmobile/constants.yaml
```

If you want to visualize your nodes, you can run the ROS visualizer or image_view.

```bash
rosrun rviz rviz
rosrun image_view image_view image:=some_imgmsg
```

In it, you can, for instance, create an 'image' instance, and set it to the
value of the `/image_const` being broadcast. This will display the image.

To load the buzzmobile mission control, simply run the node:

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

Note that `/dev/ttyUSB0` and `/dev/ttyACM0` are the default serial ports for GPS and Lidar respectively. These may or may not be different. Here are some useful commands for debugging if things aren't set up correctly:

```bash
ls -l /dev/ttyACM0  # List permissions. Will output failure if /dev/ttyACM0 is not set.
sudo chmod a+rw /dev/ttyACM0  # Sets read/write permissions for all users, not recommended.
```

Recording
---------

If you want to record the messages being outputted by certain nodes, you can use rosbag:

```
mkdir ~/bagfiles
cd ~/bagfiles
rosbag record -O filename /message/name
```

To see info about the recorded data, do `rosbag info filename.bag`

To play the data (and publish those messages), do `rosbag play test.bag`

To see your video (if you recorded camera data), do `rqt_image_view` (rqt comes with ROS if your download the desktop version), play the data if it isn't already playing, hit the refresh button at the top, and then search for the topic your .bag file is publishing to. Your camera data will play in that window.

Starting Car
------------

To start car and prepare it for driving, perform the following steps:

1. Connect the battery
2. Flip the switch inside to turn the car on
3. Ensure all e-stops are disabled. (Red buttons on front and back in out position and enabled via remote)
4. Press the green button to start the motors (Car is now live)
5. The car starts in START mode where it receives no information. It must be switched to MANUAL or AUTO for it to drive. 
6. See "Manual Mode Controls" for details on switching modes and operating the car.

Manual Mode Controls
--------------------

The `controller_node` node outputs a CarPose message and a CarState message determined by input from a PS4 controller. To control these messages and operate the car manually using the controller, use the following controls:

- Left Joystick: Change steering angle
- R2 (Right Trigger): Change velocity
- Square: Enable reverse. When this is held down, velocity is negated meaning the car will accelerate backwards.
- X: Honk the horn
- Home Button: Switch the car between AUTO and MANUAL modes.

The car starts in START mode. When pressed it will switch to MANUAL mode. Every subsequent press toggles between AUTO and MANUAL mode.
