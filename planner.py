# Type of planner
POINT_PLANNER=0; TRAJECTORY_PLANNER=1
traj_points=[]
import numpy as np
import math

class planner:
    def __init__(self, type_):

        self.type=type_

    
    def plan(self, goalPoint=[-2.0, -1.0]):
        
        if self.type==POINT_PLANNER:
            return self.point_planner(goalPoint)
        
        elif self.type==TRAJECTORY_PLANNER:
            return self.trajectory_planner()


    def point_planner(self, goalPoint):
        x = goalPoint[0]
        y = goalPoint[1]
        return x, y

    # TODO Part 6: Implement the trajectories here
    def trajectory_planner(self):
        pass
        # the return should be a list of trajectory points: [ [x1,y1], ..., [xn,yn]]
        # return 
        x_vals = np.linspace(-1, 1, 50)        # smooth curve (75 points)
        for x in x_vals:
            y = -3 + x ** 2 
            traj_points.append([x, y])

        
       # x_vals = np.linspace(-1, 1, 100)
        #for x in x_vals:
         #    y = 2.0 / (1.0 + math.exp(-2.0 * x)) - 1.0
          #   traj_points.append([x, y])
        return traj_points

