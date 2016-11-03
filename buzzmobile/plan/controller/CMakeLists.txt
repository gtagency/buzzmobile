add_executable(controller_node src/controller.cpp)
target_link_libraries(controller_node ${catkin_LIBRARIES} ${OpenCV_LIBS})
add_dependencies(controller_node ${catkin_EXPORTED_TARGETS}) 
