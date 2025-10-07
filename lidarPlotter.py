# This programs reads LIDAR scan data from a CSV file and plots the first recorded scan in Cartesian coordinates
# It should be noted that in the CSV file, the formatting requried using regex operations in order to extract the required data
# which was not ideal but the printing to CSV will be fixed for the next lab. The data extraction was the most difficult part of this code
# The CSV file data was kept as is so tht we could use the lab data instead of simulated data that wouldn't plot the lab environment

#Importing the required libraries
import re
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt

def read_lidar_csv(filename): #Function to read the LIDAR CSV file
    with open(filename, 'r') as file: #Open the file in read mode as we don't need to edit the data
        read_first_line = file.readline()  # skip header line which isn't used in plotting
        lidar_data_line_one = file.readline() # read the first data line from the CSV file

        array_match = re.search(r'\[([^\]]+)\]', lidar_data_line_one) # Extract the array content based on the current CSV format

        ranges_str = array_match.group(1) # Extract the range data into a string 
        ranges_values = [value.strip() for value in ranges_str.split(',')] #Convert the string to a list of values that can be converted to float more easily

        ranges = [] # Making list of range values all as floats, converting 'inf' to None which will be skipped in plotting as noted in the tutorial
        for index in ranges_values: # Scan values to filter inf
            if index.lower() != 'inf':
                ranges.append(float(index)) # Add to list if not inf
            else:
                ranges.append(None) # Do not add inf values to the list

    
        increment_timestamp = lidar_data_line_one[array_match.end():] # Get the rest of the line after the ranges array which should be angle_increment and timestamp
        left_variables = re.findall(r'[-+]?\d*\.\d+|\d+', increment_timestamp) # Extract all numbers (integers and floats) from the remainder

        angle_increment = float(left_variables[0]) # First number is angle_increment
        timeStamp = float(left_variables[1]) # Second number is timestamp

        return np.array(ranges, dtype=object), angle_increment, timeStamp # Return ranges as numpy array of objects to allow None values


def polar_to_cartesian(ranges, angle_increment): #Function to convert polar coordinates to Cartesian coordinates
    x_vals = []
    y_vals = []
    angle = 0.0 # Asssuming starting angle is 0 I am not sure if this is true but may need to ask about it in the next Lab

    for range_readings in ranges: # Calculations for all cordinates
        if range_readings is not None:  # skip 'inf' readings for coordinates
            x_vals.append(range_readings * math.cos(angle)) # Formula for conversion 
            y_vals.append(range_readings * math.sin(angle)) # Formula for conversion
        angle += angle_increment # Don't skip angle increment even if reading is inf

    return np.array(x_vals), np.array(y_vals) # Return x and y as numpy arrays

def plot_lidar(x, y): #Plotting of data

    plt.scatter(x, y, s=12) # Scatter plot used
    plt.xlabel('X Position (m)') # Labels and titles and grid
    plt.ylabel('Y Position (m)')
    plt.title(f'LIDAR Plot for the Scan of the Laboratory')
    plt.axis('equal') # Equal scaling for x and y axes for better looking plpt
    plt.grid(True, linestyle='--', alpha=0.5) # Grid for better visualization
    plt.show()

if __name__ == "__main__": # Main function to handle argument parsing and calling of file in terminal

    parser = argparse.ArgumentParser(description="Pprocess some files.") # Argument parser for command line inputs
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process') # Argument for list of files
    
    args = parser.parse_args() # Pparse the arguments

    print("Plotting the following files:", args.files) # Print the files being procesed

    for filename in args.files: # Loop through each function and plot
        ranges, angle_increment, stamp = read_lidar_csv(filename)
        x, y = polar_to_cartesian(ranges, angle_increment)         
        plot_lidar(x, y)                                    





