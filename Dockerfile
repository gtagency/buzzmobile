# You can change this to any version of ubuntu with little consequence
FROM ubuntu:14.04
MAINTAINER George Burdell contactgtagency@gmail.com

# Setup catkin workspace
ENV CATKIN_WS=/root/ws_moveit
RUN mkdir -p $CATKIN_WS/src
WORKDIR $CATKIN_WS/src

# Setup apt to be happy with no console input
ENV DEBIAN_FRONTEND noninteractive

# setup apt tools and other goodies we want
RUN apt-get update --fix-missing && apt-get -y install apt-utils wget curl iputils-ping vim-nox debconf-utils git software-properties-common bsdmainutils sudo && apt-get clean

# This image is not meant to be run directly, it has not been compiled yet!
# In addition, it does not contain any source code, only dependencies
