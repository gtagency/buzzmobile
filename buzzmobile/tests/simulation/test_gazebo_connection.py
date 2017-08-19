"""Simple simulation test to connect to Gazebo."""

import time

from rosgraph_msgs.msg import Clock

from pyrostest import RosTest, with_launch_file

class TestGazeboConnection(RosTest):
    """Tests for simulation testing infrastructure."""

    @with_launch_file('buzzmobile', 'simulation_test.launch')
    def test_clock_runs(self):
        """Test that simulation.launch correctly launches gazebo"""
        with self.check_topic('/clock', Clock) as ct:
            assert(ct.message)

        time.sleep(.1)
        with self.check_topic('/clock', Clock, timeout=20) as ct1:
            assert(ct1.message)
