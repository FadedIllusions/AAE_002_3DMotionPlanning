from queue import PriorityQueue
from enum import Enum
import numpy as np


def create_grid(data, drone_altitude, safety_distance):
    """
    Returns A Grid Representation Of A 2D Configuration Space Based
    On Given Obstacle Data, Drone Altitude, And A Safety Distance.
    """

    # Min/Max Coordinates
    north_min = np.floor(np.min(data[:,0] - data[:,3]))
    north_max = np.ceil(np.max(data[:,0] + data[:,3]))
    east_min = np.floor(np.min(data[:,1] - data[:,4]))
    east_max = np.ceil(np.max(data[:,1] + data[:,4]))

    # Calculate Grid Size
    north_size = int(np.ceil(north_max-north_min))
    east_size = int(np.ceil(east_max-east_min))

    # Init Empty Grid
    grid = np.zeros((north_size, east_size))

    # Populate Grid With Obstacles
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i,:]
        if alt + d_alt + safety_distance > drone_altitude:
            obstacle = [
                int(np.clip(north - d_north - safety_distance - north_min, 0, north_size-1)),
                int(np.clip(north + d_north + safety_distance - north_min, 0, north_size-1)),
                int(np.clip(east - d_east - safety_distance - east_min, 0, north_size-1)),
                int(np.clip(east - d_east + safety_distance - east_min, 0, north_size-1)),
            ]
            grid[obstacle[0]:obstacle[1]+1, obstacle[2]:obstacle[3]+1] = 1

    return grid, int(north_min), int(east_min)


# Assume All Actions Have Same Cost
class Action(Enum):
    """
    Action Represented By 3-Element Tuple

    First 2 Values Are The Delta Of Action Relative To Current Position.
    Third Value Is Cost Of Performing Action
    """

    WEST = (0, -1, 1)
    EAST = (0, 1, 1)
    NORTH = (-1, 0, 1)
    SOUTH = (1, 0, 1)

    @property
    def cost(self):
        return self.value[2]

    @property
    def delta(self):
        return (self.value[0], self.value[1])


def valid_actions(grid, current_node):
    """
    Returns List Of Valid Actions Given Current Node
    """

    valid_actions = list(Action)
    n, m = grid.shape[0]-1, grid.shape[1]-1
    x, y = current_node

    # Check If Node Off Grid Or An Obstacle
    if x-1<0 or grid[x-1, y] == 1:
        valid_actions.remove(Action.NORTH)
    if x+1>n or grid[x+1, y] == 1:
        valid_actions.remove(Action.SOUTH)
    if y-1<0 or grid[x, y-1] == 1:
        valid_actions.remove(Action.WEST)
    if y+1>m or grid[x, y+1] == 1:
        valid_actions.remove(Action.EAST)

    return valid_actions


def a_star(grid, h, start, goal):

    path = []
    path_cost = 0
    queue = PriorityQueue()
    queue.put((0, start))
    visited = set(start)

    branch = {}
    found = False
    
    while not queue.empty():
        item = queue.get()
        current_node = item[1]
        if current_node == start:
            current_cost = 0.0
        else:              
            current_cost = branch[current_node][0]
            
        if current_node == goal:        
            print('Found A Path!.')
            found = True
            break
        else:
            for action in valid_actions(grid, current_node):
                da = action.delta
                next_node = (current_node[0] + da[0], current_node[1] + da[1])
                branch_cost = current_cost + action.cost
                queue_cost = branch_cost + h(next_node, goal)
                
                if next_node not in visited:                
                    visited.add(next_node)               
                    branch[next_node] = (branch_cost, current_node, action)
                    queue.put((queue_cost, next_node))
             
    if found:
        # Retrace Steps
        n = goal
        path_cost = branch[n][0]
        path.append(goal)
        while branch[n][1] != start:
            path.append(branch[n][1])
            n = branch[n][1]
        path.append(branch[n][1])
    else:
        print('**********************')
        print('Failed To Find A Path!')
        print('**********************') 
    return path[::-1], path_cost


def heuristic(position, goal_position):
    return np.linalg.norm(np.array(position) - np.array(goal_position))


def point(p):
    return np.array([p[0], p[1], 1.]).reshape(1, -1)


def collinearity_check(p1, p2, p3, epsilon=1e-6)
    m = np.concatenate((p1, p2, p3), 0)
    det = np.linalg.det(m)
    return np.abs(det) < epsilon


def prune_path(path):
    if path is not None:
        pruned_path = [p for p in path]

        i = 0
        while i < len(pruned_path)-2:
            p1 = point(pruned_path[i])
            p2 = point(pruned_path[i+1])
            p3 = point(pruned_path[i+2])

            if collinearity_check(p1, p2, p3):
                pruned_path.remove(pruned_path[i+1])
            else:
                i += 1

    return pruned_path



