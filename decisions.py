# Imports


import sys

from utilities import euler_from_quaternion, calculate_angular_error, calculate_linear_error
from pid import PID_ctrl

from rclpy import init, spin, spin_once
from rclpy.node import Node
from geometry_msgs.msg import Twist

from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import Odometry as odom

from localization import localization, rawSensor

from planner import TRAJECTORY_PLANNER, POINT_PLANNER, planner
from controller import controller, trajectoryController

DISTANCE_TOLERANCE=0.05 # This is the constant value we used for the linear distance tolerance compared to the goal point
ANGLE_TOLERANCE=0.10 # This is the constant value we used for the angular tolerance compared to the goal point


# You may add any other imports you may need/want to use below
# import ...



class decision_maker(Node):
    
    def __init__(self, publisher_msg, publishing_topic, qos_publisher, goalPoint, rate=10, motion_type=POINT_PLANNER):

        super().__init__("decision_maker")

        #TODO Part 4: Create a publisher for the topic responsible for robot's motion
        self.publisher=self.create_publisher(Twist, '/cmd_vel', 10) #Created a publisher responsible for the robots motion
        

        publishing_period=1/rate
        
        # Instantiate the controller
        # TODO Part 5: Tune your parameters here
    
        # We left these values as provided to us for now and plan to tune them on the real robot in the lab

        if motion_type == POINT_PLANNER:
            self.controller=controller(klp=0.2, klv=0.5, kap=0.8, kav=0.6)
            self.planner=planner(POINT_PLANNER)   
    
    
        elif motion_type==TRAJECTORY_PLANNER:
            self.controller=trajectoryController(klp=0.2, klv=0.5, kap=0.8, kav=0.6)
            self.planner=planner(TRAJECTORY_PLANNER)

        else:
            print("Error! you don't have this planner", file=sys.stderr)


        # Instantiate the localization, use rawSensor for now  
        self.localizer=localization(rawSensor) # Create a class variable based on rawSensor for the localization
        
        

        # Instantiate the planner
        # NOTE: goalPoint is used only for the pointPlanner
        self.goal=self.planner.plan(goalPoint)
        
        self.create_timer(publishing_period, self.timerCallback)
        
        


    def timerCallback(self):
        
        # TODO Part 3: Run the localization node
        # Remember that this file is already running the decision_maker node.
        
        spin_once(self.localizer, timeout_sec=0.0) #Running the localization node once
      
        if self.localizer.getPose()  is  None:
            print("waiting for odom msgs ....")
            return

        vel_msg=Twist()
        if type(self.goal) == list:
            final_goal=self.goal[-1]
        else:
            final_goal=self.goal
        linear_error = calculate_linear_error(self.localizer.getPose(), final_goal)
        angular_error = calculate_angular_error(self.localizer.getPose(), final_goal)
        print("Linear Error:", linear_error)
        print("Angular Error:", angular_error)

        # TODO Part 3: Check if you reached the goal

        if type(self.goal) == list:
            reached_goal = (linear_error < DISTANCE_TOLERANCE) and (abs(angular_error) < ANGLE_TOLERANCE) # Checks if within linear and angular tolerances
        else: 
            reached_goal = (linear_error < DISTANCE_TOLERANCE) # Linear error less than tolerance
        

        if reached_goal:
            print("reached goal")
            self.publisher.publish(vel_msg)
            
            self.controller.PID_angular.logger.save_log()
            self.controller.PID_linear.logger.save_log()
            
            #TODO Part 3: exit the spin

            raise SystemExit #Exception has been raised to exit the spin once goal is reached
        
        velocity, yaw_rate = self.controller.vel_request(self.localizer.getPose(), self.goal, True)

        #TODO Part 4: Publish the velocity to move the robot
        vel_msg.linear.x = float(velocity) # Add the velocity to the linear variable of the overall velocity message
        #print("velocity:", velocity) # Optional test print for debugging
        vel_msg.angular.z = float(yaw_rate) # Add the yaw to the angular variable of the overall velocity message
        #print("yaw_rate:", yaw_rate) # Optional test print for debugging
        
        self.publisher.publish(vel_msg) # Publish the full velocity package to move the robot (as in lab 1)

import argparse


def main(args=None):

    init()
    # TODO Part 3: You migh need to change the QoS profile based on whether you're using the real robot or in simulation.
    # Remember to define your QoS profile based on the information available in "ros2 topic info /odom --verbose" as explained in Tutorial 3

    USING_SIM = True # Boolean variable to switch between sim and real robot
    
    #ros2 topic info /odom --verbose # run this command in terminal to get the values for both sim and real robot

    if USING_SIM: # QoS profile for simulation (variables set accordinging to terminal command output)
        odom_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=1,
            depth=10
        )
    #else: # QoS profile for real robot (these variables will be used during the lab when USING_SIM is set to False)
    #        odom_qos = QoSProfile(
    #            reliability=QoSReliabilityPolicy.FoundVal,
    #            durability=QoSDurabilityPolicy.FoundVal,
    #            history=QoSHistoryPolicy.FoundVal,
    #            depth=FoundVal
    #)
    
    # TODO Part 4: instantiate the decision_maker with the proper parameters for moving the robot
    if args.motion.lower() == "point":
        DM=decision_maker(Twist, '/cmd_vel', odom_qos, planner(POINT_PLANNER).plan(), 10, POINT_PLANNER) # Call decision maker class with the required inputs for the point motion
    elif args.motion.lower() == "trajectory":
        DM=decision_maker(Twist, '/cmd_vel', odom_qos, planner(TRAJECTORY_PLANNER).plan(), 10, TRAJECTORY_PLANNER) # Call decision maker class with the required inputs for the trajectory motion
    else:
        print("invalid motion type", file=sys.stderr)
    
    
    try:
        spin(DM)
    except SystemExit:
        
        print(f"reached there successfully {DM.localizer.pose}")



if __name__=="__main__":

    argParser=argparse.ArgumentParser(description="point or trajectory") 
    argParser.add_argument("--motion", type=str, default="point")
    args = argParser.parse_args()

    main(args)
