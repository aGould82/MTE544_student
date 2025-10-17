import sys

from utilities import Logger, euler_from_quaternion
from rclpy.time import Time
from rclpy.node import Node

from rclpy.qos import QoSProfile
from nav_msgs.msg import Odometry as odom

from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from rclpy import init, spin, shutdown

rawSensor = 0
class localization(Node):
    
    def __init__(self, localizationType=rawSensor):

        super().__init__("localizer")
        
        # TODO Part 3: Define the QoS profile variable based on whether you are using the simulation (Turtlebot 3 Burger) or the real robot (Turtlebot 4)
        # Remember to define your QoS profile based on the information available in "ros2 topic info /odom --verbose" as explained in Tutorial 3
       

        # Process below when we have the program running:

        # need to run the following in terminal: ros2 topic info /odom --verbose
        # will receive reliability, durability, history and depth values for both simulation and real robot

        # The code below sets the qos profile based on the data retrieved from the terminal command above

        #Part3 code modified below
        
       # Can use the following logic after doing the initial search for the qos profile values based on sim or real

        USING_SIM = True
        #ros2 topic info /odom --verbose # run this command in terminal to get the values for both sim and real robot
        #from rclpy.qos import QoSProfile, QosReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

        if USING_SIM:
            odom_qos = QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
                history=1,
                depth=10
            )
        #else:
            
        #    odom_qos = QoSProfile(
        #        reliability=QoSReliabilityPolicy.FoundVal,
        #        durability=QoSDurabilityPolicy.FoundVal,
        #        history=QoSHistoryPolicy.FoundVal,
        #        depth=FoundVal
        #    )
        

        #odom_qos=...
        
        self.loc_logger=Logger("robot_pose.csv", ["x", "y", "theta", "stamp"])
        self.pose=None
        
        if localizationType == rawSensor:
        # TODO Part 3: subscribe to the position sensor topic (Odometry)

            #Part3 code modified below
            self.create_subscription(odom, '/odom', self.odom_callback, odom_qos) # for reading the data from odometry messages from tutorial 3

        else:
            print("This type doesn't exist", sys.stderr)
    
    
    def odom_callback(self, pose_msg):
        
        # TODO Part 3: Read x,y, theta, and record the stamp
        
        #Part3 code modified below
        timestamp = pose_msg.header.stamp  #get time stamp in nanoseconds
        odom_x_pos = pose_msg.pose.pose.position.x #to record odometry x position
        odom_y_pos = pose_msg.pose.pose.position.y #to record odometry y position
        q = pose_msg.pose.pose.orientation
        theta = euler_from_quaternion([q.x,q.y, q.z, q.w])
        
        self.pose=[odom_x_pos, odom_y_pos, theta, timestamp]

        # Log the data
        self.loc_logger.log_values([self.pose[0], self.pose[1], self.pose[2], Time.from_msg(self.pose[3]).nanoseconds])
    
        

    def getPose(self):
        return self.pose

# TODO Part 3
# Here put a guard that makes the node run, ONLY when run as a main thread!
# This is to make sure this node functions right before using it in decision.py
#Part3 code modified below

def main(args=None):
    print("3")
    init(args=args)
    node = localization()
    spin(node)
    #node.destroy_node() # Don't need to add
    #shutdown() # Don't need to add

if __name__ == "__main__":
    main()