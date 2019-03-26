from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
from heapq import *
from math import sqrt

ACTIONS = [(0,-1),(-1,0),(0,1),(1,0)]

class Agent:
    def __init__(self, grid, start, goal, type):
        self.grid = grid
        self.previous = {}
        self.explored = []
        self.start = start 
        self.grid.nodes[start].start = True
        self.goal = goal
        self.grid.nodes[goal].goal = True
        self.new_plan(type)
        self.iteration = 0
    def new_plan(self, type):
        self.finished = False
        self.failed = False
        self.type = type
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.explored = []
        elif self.type == "bfs":
            self.frontier = [self.start]
            self.explored  = []
            pass
        elif self.type == "ucs":
            self.frontier = []
            # Add self.start to frontier with priority of 0
            heappush(self.frontier, (0, self.start))
            self.explored = []
            # Set G cost of start to 0, chose to include a separate array because wanted to have a way to easily get the path costs of the children nodes 
            # when relaxing edges
            self.costArr = {self.start: 0}
            pass
        elif self.type == "astar":
            self.frontier = []
            # Add self.start to frontier with priority of 0, store cost 
            heappush(self.frontier, (self.heuristic_manhattan(self.start, self.goal), self.start))
            self.explored = []
            # Set G cost of start to 0
            self.costArr = {self.start: 0}
            pass
    def show_result(self):
        current = self.goal
        while not current == self.start:
            current = self.previous[current]
            self.grid.nodes[current].in_path = True #This turns the color of the node to red
    def make_step(self):
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
    def dfs_step(self):
        # If frontier is empty then there is no path so return failed
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("current node: ", current)
        # Mark current node as checked and remove from frontier
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        # Go through each node in children
        for node in children:
            # If node has been explored or is in the frontier skip the node
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            # Check if node is in the range of the grid
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                # If node is a puddle then skip
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    # Set the previous of node to current, if node is goal then return finished
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        # Add node to frontier
                        self.frontier.append(node)
                        # Set node frontier flag to true
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)

    def bfs_step(self):
        # If frontier is empty then there is no path so return failed
        if not self.frontier:
            self.failed = True
            print("No path")
            return
        current = self.frontier.pop()
        print("current node: ", current)
        # Mark current node as checked and remove from frontier
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]

        for node in children:
            # If node has been explored or is in the frontier skip the node
            if node in self.explored or node in self.frontier:
                print("expored before: ", node)
                continue
            # Check if node is in the range of the grid
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                # If node is a puddle then skip
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    # Set the previous of node to current, if node is goal then return finished, else enqueue to frontier
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        self.frontier = [node] + self.frontier
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)
                    
    def ucs_step(self):
        # If frontier is empty then there is no path so return failed
        if not self.frontier: 
            self.failed = True
            print("No path")
            return
        # Pop node from frontier with lowest G cost
        nodeVal = heappop(self.frontier)
        current = nodeVal[1]
        # Get G cost for the current node
        currentCost = self.costArr[current]
        # Mark node as in frontier and is checked
        self.grid.nodes[current].frontier = False
        self.grid.nodes[current].checked = True
        # If node is goal print cost for path and return true
        if current == self.goal:
            print("Current cost is: " + str(currentCost))
            self.finished = True
            return

        # Add node to explored
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        # For each child of node 
        for node in children:
            # If node is in range of the grid
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                # If node is a puddle then skip
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    # Get G_temp and store in altCost
                    altCost = currentCost + self.grid.nodes[node].cost()
                    # If not has not been explored and is not in frontier, then add node in frontier, this check prevents adding duplicates to frontier
                    if node not in self.explored and not self.grid.nodes[node].frontier:
                        # Add to frontier with altCost priority, store altCost node in G array, set current to previous of node, and set frontier to true
                        heappush(self.frontier, (altCost, node))
                        self.costArr[node] = altCost
                        self.previous[node] = current
                        self.grid.nodes[node].frontier = True 
                    # If node is in frontier and the cost you found is cheaper than cost previously found, relax that edge
                    elif self.grid.nodes[node].frontier and self.costArr[node] > altCost:
                        i = 0
                        # Find node and remove it from frontier
                        while i < len(self.frontier):
                            if(self.frontier[i][1] == node):
                                self.frontier[i] = self.frontier[-1]
                                self.frontier.pop()
                                break
                            i += 1
                        # Heapify frontier and add node to frontier with priority of altCost, store new cost in G array, and update previous of node to current
                        heapify(self.frontier)
                        heappush(self.frontier, (altCost, node))
                        self.costArr[node] = altCost
                        self.previous[node] = current
            else:
                print("out of range: ", node)
        
    def astar_step(self):
        heuristic_weight = 10
        # If frontier is empty then there is no path so return failed
        if not self.frontier: 
            self.failed = True
            print("No path")
            return
        # Pop node from frontier with lowest F cost, where F = G + H
        nodeVal = heappop(self.frontier)
        current = nodeVal[1]
        # Retrieve G cost for current
        currentCost = self.costArr[current]
        # Mark node as being in frontier and mark it as checked
        self.grid.nodes[current].frontier = False
        self.grid.nodes[current].checked = True
        # If node is goal print cost for path and return true
        if current == self.goal:
            print("Current cost is: " + str(currentCost))
            self.finished = True
            return

        # Add node to explored
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        for node in children:
            # If node is in range of the grid
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                # If node is a puddle then skip
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    # Get G_temp and store in altCost
                    altCost = currentCost + self.grid.nodes[node].cost()
                    # If not has not been explored and is not in frontier, then add node in frontier, this check prevents adding duplicates to frontier
                    if node not in self.explored and not self.grid.nodes[node].frontier:
                        # Add to frontier with F = G + H priority, store altCost node in G array, set current to previous of node, and set frontier to true
                        heappush(self.frontier, (altCost + heuristic_weight*self.heuristic_manhattan(node, self.goal), node))
                        self.costArr[node] = altCost
                        self.previous[node] = current
                        self.grid.nodes[node].frontier = True
                    # If node is in frontier and the cost you found is cheaper than cost previously found, relax that edge
                    elif self.grid.nodes[node].frontier and self.costArr[node] > altCost:
                        i = 0
                        # Find node and remove it from frontier
                        while i < len(self.frontier):
                            if(self.frontier[i][1] == node):
                                self.frontier[i] = self.frontier[-1]
                                self.frontier.pop()
                                break
                            i += 1
                        # Heapify frontier and add node to frontier with priority of G + H, store new cost in G array, and update previous of node to current
                        heapify(self.frontier)
                        heappush(self.frontier, (altCost + heuristic_weight*self.heuristic_manhattan(node, self.goal), node))
                        self.costArr[node] = altCost
                        self.previous[node] = current
            else:
                print("out of range: ", node)

    # Heuristic function implemented using manhattan distance, returning the sum of the absolute differences of the x and y coordinates
    def heuristic_manhattan(self, node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
        
