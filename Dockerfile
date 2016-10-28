# You can change this to any version of ubuntu with little consequence
FROM ubuntu:14.04
MAINTAINER George Burdell contactgtagency@gmail.com

# Setup apt to be happy with no console input
ENV DEBIAN_FRONTEND noninteractive

# setup apt tools and other goodies we want
RUN apt-get update --fix-missing && apt-get -y install apt-utils wget curl iputils-ping vim-nox debconf-utils git software-properties-common bsdmainutils sudo && apt-get clean

# set up user that can use rosdep update without sudo
# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer && mkdir -p /etc/udev/rules.d/

USER developer
ENV HOME /home/developer

# do everything in root's home
RUN mkdir -p /home/developer/catkin_ws/src/buzzmobile
WORKDIR /home/developer/catkin_ws/src/buzzmobile

# This image is not meant to be run directly, it has not been compiled yet!
# In addition, it does not contain any source code, only dependencies
