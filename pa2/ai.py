from __future__ import absolute_import, division, print_function
import copy
import random
import collections
import operator
import sys
import math
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}

class Gametree:
	"""main class for the AI"""
	def __init__(self, root_state, depth_of_tree, current_score): 
		# Set depth of tree
		self.depth_of_tree = depth_of_tree
		# Set directions 
		self.directions = [0, 1, 2, 3]
		# Initialize root of tree
		self.root = Node(root_state, True, current_score, -1, 0)
		# Grow tree from constructor
		self.growTree(self.root, 0)

	# In charge of growing the game tree
	def growTree(self, node, depth):
		# If you've reached the desired depth then return
		if(depth == self.depth_of_tree):
			return
		# If node is max player
		if(node.isMaxPlayer()):
			# Simulate moving in the four directions and make a chance child node if the board is unique
			for dir in self.directions:
				sim = Simulator(copy.deepcopy(node.getBoardState()), node.getPoints())
				sim.move(dir)
				# Check for unique board states
				if(sim.getState() != node.getBoardState()):
					newNode = Node(sim.getState(), False, sim.getPoints(), dir, depth + 1)
					node.addChild(newNode)
		# Else if the node is a chance player then randomly choose a spot to add a tile and add it as a max player
		elif(node.isChancePlayer()):
			# Get empty spots for the board
			emptySpots = self.getEmptySpots(node.getBoardState())
			# Creating a max player for each empty spot
			for spot in emptySpots:
				board_copy = copy.deepcopy(node.getBoardState())
				board_copy[spot[0]][spot[1]] = 2
				newNode = Node(board_copy, True, node.getPoints(), -1, depth + 1)
				node.addChild(newNode)
		# Call grow tree on every child
		for child in node.getChildren():
			self.growTree(child, depth + 1) 

	# Takes in a board and returns the empty spots for the board
	def getEmptySpots(self, matrix):
		zeroPoints = []
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				if(matrix[i][j] == 0):
					zeroPoints.append((i, j))
		return zeroPoints

	# Helper function to visualize tree
	def printTreeLevelOrder(self):
		self.printNodes(self.root)
	
	def printNodes(self, node):
		print("Parent: ", node.isMaxPlayer(), node.getPoints(), node.getDepth(), node.getDirection())
		print("Children: ")
		self.printChildren(node)
		for child in node.getChildren():
			self.printNodes2(child)

	def printChildren(self, node):
		counter = 0
		for child in node.getChildren():
			print(counter, child.isMaxPlayer(), child.getPoints(), child.getDepth(), child.getDirection())
			counter += 1

	# expectimax for computing best move
	def expectimax(self, node):
		# If terminal node then return the payoff for the node
		if len(node.getChildren()) == 0:
			payoff = self.payoff(node)
			node.setExpectimax(payoff)
			return payoff
		# If maxPlayer then get the max expectimax value from all of its children and return that value
		elif node.isMaxPlayer():
			value = -sys.maxsize - 1 
			for child in node.getChildren():
				value = max(value, self.expectimax(child))
			node.setExpectimax(value)
			return value
		# If chance player calculate the average of each of the children
		elif node.isChancePlayer():
			value = 0
			for child in node.getChildren():
				value += self.expectimax(child)*(1.0/len(node.getChildren()))
			node.setExpectimax(value)
			return value
		else:
			print("Error")
			return -1


	# Payoff function to calculate score for board
	def payoff(self, node):
		numZeros = 0
		# Count number of zeros on the board
		for i in range(len(node.getBoardState())):
			for j in range(len(node.getBoardState()[i])):
				if(node.getBoardState()[i][j] == 0):
					numZeros+=1

		# Calculate monoticity score for board
		sum = 0
		board = node.getBoardState()
		for j in range(len(board)):
			for i in range(3):
				sum += board[i + 1][j] - board[i][j]
		for j in range(len(board)):
			for i in range(3):
				sum += board[j][i + 1] - board[j][i]

		# Payoff function is a combination of the monoticity sum, the points, and the number of empty spots
		return sum + node.getPoints() + numZeros

	# function to return best decision to game
	def compute_decision(self):
		# Get optimal expectimax score
		optimalVal = self.expectimax(self.root)
		# Choose the direction that gives the optimalVal calculated
		for child in self.root.getChildren():
			if child.getExpectimax() == optimalVal:
				return child.getDirection()
		return 0

class Node:
	'''Node class for gametree '''
	def __init__(self, board_state, is_max_player, board_score, direction, depth):
		# Save board state, max player, board score, direction and depth for the node
		self.board_state = board_state
		self.is_max_player = is_max_player
		self.board_score = board_score
		self.expectimax = board_score
		self.direction = direction
		self.children = []
		self.depth = depth
	
	# Returns true if node is a max player
	def isMaxPlayer(self):
		return self.is_max_player
	
	# Returns true if node is a chance player
	def isChancePlayer(self):
		return not self.is_max_player
	
	# Returns board state for the node
	def getBoardState(self):
		return self.board_state

	# Returns points for the node
	def getPoints(self):
		return self.board_score
	
	# Returns direction for the node
	def getDirection(self):
		return self.direction

	# Sets expectimax for the node
	def setExpectimax(self, val):
		self.expectimax = val
	
	# Returns expectimax for the node
	def getExpectimax(self):
		return self.expectimax

	# Adds child to the node
	def addChild(self, child):
		self.children.append(child)
	
	# Returns children of node
	def getChildren(self):
		return self.children

	# Returns depth of node
	def getDepth(self):
		return self.depth

class Simulator:
	'''Simulator class to simulate moves'''
	def __init__(self, board_state, total_points):
		# Takes in board state and total_points
		self.board_state = board_state
		self.board_size = 4
		self.total_points = total_points
	
	def move(self, direction):
		for i in range(0, direction):
			self.rotateMatrixClockwise(self.board_state)
		if self.canMove(self.board_state):
			self.moveTiles(self.board_state)
			self.mergeTiles(self.board_state)
			self.placeRandomTile(self.board_state)
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise(self.board_state)

	def getState(self):
		return self.board_state

	def getPoints(self):
		return self.total_points

	def rotateMatrixClockwise(self, tileMatrix):
		tm = tileMatrix
		for i in range(0, int(self.board_size/2)):
			for k in range(i, self.board_size- i - 1):
				temp1 = tm[i][k]
				temp2 = tm[self.board_size - 1 - k][i]
				temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
				temp4 = tm[k][self.board_size - 1 - i]
				tm[self.board_size - 1 - k][i] = temp1
				tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
				tm[k][self.board_size - 1 - i] = temp3
				tm[i][k] = temp4

	def canMove(self, tileMatrix):
		tm = tileMatrix
		for i in range(0, self.board_size):
			for j in range(1, self.board_size):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False

	def moveTiles(self, tileMatrix):
		tm = tileMatrix
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, self.board_size - 1):
						tm[i][k] = tm[i][k + 1]
					tm[i][self.board_size - 1] = 0
	
	def mergeTiles(self, tileMatrix):
		tm = tileMatrix
		for i in range(0, self.board_size):
			for k in range(0, self.board_size - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.total_points += tm[i][k]
					self.moveTiles(tileMatrix)
	
	def placeRandomTile(self, tileMatrix):
		while True:
			i = random.randint(0,self.board_size-1)
			j = random.randint(0,self.board_size-1)
			if tileMatrix[i][j] == 0:
				break
		tileMatrix[i][j] = 2


