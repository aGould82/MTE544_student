# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile

# TODO Part 3: Import message types needed: 
    # For sending velocity commands to the robot: Twist
    # For the sensors: Imu, LaserScan, and Odometry
# Check the online documentation to fill in the lines below

from geometry_msgs.msg import Twist # for sending velocity commands to the robot found from terminal commands
from sensor_msgs.msg import Imu
from sensor_msgs.msg import LaserScan # for reading laser data found from terminal commands
from nav_msgs.msg import Odometry # for reading odometry data found from terminal commands

from rclpy.time import Time 

# You may add any other imports you may need/want to use below
# import ...

from utilities import log_values #importing the log values function to pass values to the utilities file
temp = 0 # variable to help with spiral motion

CIRCLE=0; SPIRAL=1; ACC_LINE=2
motion_types=['circle', 'spiral', 'line']

class motion_executioner(Node):
    
    def __init__(self, motion_type=0):
        
        super().__init__("motion_types")
        
        self.type=motion_type
        
        self.radius_=0.0
        
        self.successful_init=False
        self.imu_initialized=False
        self.odom_initialized=False
        self.laser_initialized=False
        
        # TODO Part 3: Create a publisher to send velocity commands by setting the proper parameters in (...)
        self.vel_publisher=self.create_publisher(Twist, '/cmd_vel', 10) # publisher to send velocity commands found in tutorial 3
                
        # loggers
        self.imu_logger=Logger('imu_content_'+str(motion_types[motion_type])+'.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger=Logger('odom_content_'+str(motion_types[motion_type])+'.csv', headers=["x","y","th", "stamp"])
        self.laser_logger=Logger('laser_content_'+str(motion_types[motion_type])+'.csv', headers=["ranges", "angle_increment", "stamp"])
        
        # TODO Part 3: Create the QoS profile by setting the proper parameters in (...)
        qos=QoSProfile(reliability=2, durability=2, history=1, depth=10) # create the QoS profile found in tutorial 3

        # TODO Part 5: Create below the subscription to the topics corresponding to the respective sensors
        # IMU subscription
        
        self.create_subscription(Imu, '/imu', self.imu_callback, 10) # for reading the data from imu messages from tutorial 3
        
        # ENCODER subscription

        self.create_subscription(Odometry, '/odom', self.odom_callback, 10) # for reading the data from odometry messages from tutorial 3
        
        # LaserScan subscription 
        
        self.create_subscription(LaserScan, '/scan', self.laser_callback, 10) # for reading the data from laser scan messages from tutorial 3
        
        self.create_timer(0.1, self.timer_callback)


    # TODO Part 5: Callback functions: complete the callback functions of the three sensors to log the proper data.
    # To also log the time you need to use the rclpy Time class, each ros msg will come with a header, and then
    # inside the header you have a stamp that has the time in seconds and nanoseconds, you should log it in nanoseconds as 
    # such: Time.from_msg(imu_msg.header.stamp).nanoseconds
    # You can save the needed fields into a list, and pass the list to the log_values function in utilities.py

    def imu_callback(self, imu_msg: Imu):
        # log imu msgs
        timestamp = Time.from_msg(imu_msg.header.stamp) .nanoseconds  #get time stamp in nanoseconds
        
        imu_orientation=imu_msg.orientation #to record imu orientation 
        imu_x_orientation = imu_orientation.x #to record imu x position
        imu_y_orientation = imu_orientation.y #to record imu y position

        imu_angular_velocity=imu_msg.angular_velocity #to record imu angular velocity
        log_values[imu_angular_velocity.x, imu_angular_velocity.y, imu_angular_velocity.z, timestamp] # logging the list of message values to be used in utilities.py
        
        #print all recorded message values
        print(f'Message Timestamp = {timestamp}')
        print(f'Current IMU Orientation = {imu_orientation}')
        print(f'Current IMU X Orientation = {imu_x_orientation}')
        print(f'Current IMU Y Orientation = {imu_y_orientation}')
        print(f'Current IMU Angular Velocity = {imu_angular_velocity}')

    def odom_callback(self, odom_msg: Odometry):
        # log odom msgs
        timestamp = Time.from_msg(odom_msg.header.stamp) .nanoseconds  #get time stamp in nanoseconds
                
        odom_orientation=odom_msg.pose.pose.orientation #to record odometry orientation
        odom_x_pos = odom_msg.pose.pose.position.x #to record odometry x position
        odom_y_pos = odom_msg.pose.pose.position.y #to record odometry y position

        log_values[odom_x_pos, odom_y_pos, odom_orientation, timestamp] # logging the list of message values to be used in utilities.py
        
        #print all recorded message values
        print(f'Message Timestamp = {timestamp}')
        print(f'Current Robot Orientation = {odom_orientation}')
        print(f'Current Robot X Position = {odom_x_pos}')
        print(f'Current Robot Y Position = {odom_y_pos}')
        
    def laser_callback(self, laser_msg: LaserScan):
        # log laser msgs with position msg at that time
        timestamp = Time.from_msg(laser_msg.header.stamp) .nanoseconds #get time stamp in nanoseconds

        laser_ranges=laser_msg.ranges #to record laser ranges
        laser_angle_min=laser_msg.angle_min #to record laser minimum angle
        laser_angle_max=laser_msg.angle_max #to record laser maximum angle

        log_values[laser_ranges, laser_angle_min, laser_angle_max, timestamp] # logging the list of message values to be used in utilities.py

        #print all recorded message values
        print(f'Message Timestamp = {timestamp}')
        print(f'Current Laser Ranges = {laser_ranges}')
        print(f'Current Laser Angle Min = {laser_angle_min}')
        print(f'Current Laser Angle Max = {laser_angle_max}')

    def timer_callback(self):
        
        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init=True
            
        if not self.successful_init:
            return
        
        cmd_vel_msg=Twist()
        
        if self.type==CIRCLE:
            cmd_vel_msg=self.make_circular_twist()
        
        elif self.type==SPIRAL:
            cmd_vel_msg=self.make_spiral_twist()
                        
        elif self.type==ACC_LINE:
            cmd_vel_msg=self.make_acc_line_twist()
            
        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit 

        self.vel_publisher.publish(cmd_vel_msg)
        
    
    # TODO Part 4: Motion functions: complete the functions to generate the proper messages corresponding to the desired motions of the robot

    def make_circular_twist(self):
        # fill up the twist msg for circular motion
        msg=Twist()
        msg.linear.x=0.5 #values taken from tutorial 3 for x linear velocity
        msg.angular.z = 0.7 #values taken from tutorial 3 for z angular velocity

        return msg

    def make_spiral_twist(self):
        # fill up the twist msg for spiral motion
        msg=Twist()

        msg.angular.z=0.7 
        
        #if statement to increment robot speed until it reach max speed and reset
        if temp <= 1:
            temp += 0.1
        else:
            temp = 0
        msg.linear.x = temp

        return msg
    
    def make_acc_line_twist(self):
        # fill up the twist msg for line motion
        msg=Twist()
        msg.linear.x=0.5 #robot to have only linear velocity for straight line motion
        msg.angular.z = 0
        return msg

import argparse

if __name__=="__main__":
    

    argParser=argparse.ArgumentParser(description="input the motion type")


    argParser.add_argument("--motion", type=str, default="circle")



    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":

        ME=motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME=motion_executioner(motion_type=ACC_LINE)

    elif args.motion.lower() =="spiral":
        ME=motion_executioner(motion_type=SPIRAL)

    else:
        print(f"we don't have {arg.motion.lower()} motion type")


    
    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
