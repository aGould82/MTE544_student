import numpy as np


from pid import PID_ctrl
from utilities import euler_from_quaternion, calculate_angular_error, calculate_linear_error

M_PI=3.1415926535

P=0; PD=1; PI=2; PID=3

goal = None # global variable to store the current goal point for trajectory controller

class controller:
    
    
    # Default gains of the controller for linear and angular motions
    def __init__(self, klp=0.2, klv=0.2, kli=0.2, kap=0.2, kav=0.2, kai=0.2):
        
        # TODO Part 5 and 6: Modify the below lines to test your PD, PI, and PID controller
        self.PID_linear=PID_ctrl(PID, klp, klv, kli, filename_="linear.csv")
        self.PID_angular=PID_ctrl(PID, kap, kav, kai, filename_="angular.csv")

    
    def vel_request(self, pose, goal, status):
        
        e_lin=calculate_linear_error(pose, goal)
        e_ang=calculate_angular_error(pose, goal)


        linear_vel=self.PID_linear.update([e_lin, pose[3]], status)
        #print("linear_vel:", linear_vel)
        angular_vel=self.PID_angular.update([e_ang, pose[3]], status)
        #print("angular_vel:", angular_vel)
        
        # TODO Part 4: Add saturation limits for the robot linear and angular velocity (hint: you can use np.clip function)
        max_lin_vel = 0.22 # 0.22 for sim 0.3 real
        
        linear_vel = np.clip(linear_vel, -max_lin_vel, max_lin_vel) #clipping linear velocity for values outside the range

        max_ang_vel = 2.84 # 2.84 for sim 1.9 real
        angular_vel= np.clip(angular_vel, -max_ang_vel, max_ang_vel)#clipping angular velocity for values outside the range
        
        return linear_vel, angular_vel
    

class trajectoryController(controller):

    def __init__(self, klp=0.2, klv=0.2, kli=0.2, kap=0.2, kav=0.2, kai=0.2):
        
        super().__init__(klp, klv, kli, kap, kav, kai)
    
    def vel_request(self, pose, listGoals, status):
        
        finalGoal=listGoals[-1]
        #we had trouble robot reaching the final goal for trajectory so we created the current goal global variable to use
        global goal
        if goal!=finalGoal: #check if the current goal is equal to the final goal if it is do not update the goal
            goal=self.lookFarFor(pose, listGoals)
        
        
        print("Current Goal:", goal)#print statments for testing
        print("Final Goal:", finalGoal)
        
        e_lin=calculate_linear_error(pose, finalGoal)
        e_ang=calculate_angular_error(pose, goal)

        
        linear_vel=self.PID_linear.update([e_lin, pose[3]], status)
        angular_vel=self.PID_angular.update([e_ang, pose[3]], status) 

        # TODO Part 5: Add saturation limits for the robot linear and angular velocity (hint: you can use np.clip function)

        max_lin_vel = 0.22 # 0.22 for sim 0.3 real
        
        linear_vel = np.clip(linear_vel, -max_lin_vel, max_lin_vel)#clipping linear velocity for values outside the range

        max_ang_vel = 2.84 # 2.84 for sim 1.9 real
        angular_vel= np.clip(angular_vel, -max_ang_vel, max_ang_vel) #clipping angular velocity for values outside the range
        
        return linear_vel, angular_vel

    def lookFarFor(self, pose, listGoals):
        
        poseArray=np.array([pose[0], pose[1]]) 
        listGoalsArray=np.array(listGoals)

        distanceSquared=np.sum((listGoalsArray-poseArray)**2,
                               axis=1)
        closestIndex=np.argmin(distanceSquared)

        return listGoals[ min(closestIndex + 3, len(listGoals) - 1) ]
