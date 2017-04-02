project(buzzmobile)
set(CMAKE_CXX_FLAGS "-std=c++11 -g ${CMAKE_CXX_FLAGS}")
list(APPEND CMAKE_MODULE_PATH $(CMAKE_CURRENT_SOURCE_DIR)/cmake)
find_package(catkin REQUIRED COMPONENTS
              roscpp
              std_msgs
              sensor_msgs
              cv_bridge
              image_transport
              message_generation
              gazebo_ros
              )
find_package(OpenCV REQUIRED)
find_package(gazebo REQUIRED)

add_message_files(
  FILES
  CarPose.msg
  CarState.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  sensor_msgs
)
catkin_package( INCLUDE_DIRS
                LIBRARIES buzzmobile
                CATKIN_DEPENDS roscpp std_msgs sensor_msgs message_runtime cv_bridge rospy
                DEPENDS system_lib gazebo_ros
)
include_directories(
                    ${catkin_INCLUDE_DIRS}
                    ${OPENCV_INCLUDE_DIRS}
                    ${GAZEBO_INCLUDE_DIRS}
                    ${SDFormat_INCLUDE_DIRS}
)

add_subdirectory(process/projector)
add_subdirectory(plan/controller)
add_subdirectory(drive/car_interface)
add_subdirectory(simulation/sim_car_interface)
