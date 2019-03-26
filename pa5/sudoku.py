from __future__ import print_function
import random, copy

class Grid:
	def __init__(self, problem):
		self.spots = [(i, j) for i in range(1,10) for j in range(1,10)]
		self.domains = dict(((i, j), range(1, 10)) for i in range(1, 10) for j in range(1, 10))
		#Need a dictionary that maps each spot to its related spots
		self.peers = {} 

		# Adding code to populate units and peers which is used in the algorithm as described in the post
		rows = [1,2,3,4,5,6,7,8,9]
		cols = rows
		unitlists = [self.crossLists(rows, [c]) for c in cols] + [self.crossLists([r], cols) for r in rows] + [self.crossLists(rs, cs) for rs in ([1,2,3], [4,5,6], [7,8,9]) for cs in ([1,2,3], [4,5,6], [7,8,9])]
		self.units = dict((s, [u for u in unitlists if s in u]) for s in self.spots)
		self.peers = dict((s, set(sum(self.units[s],[]))-set([s])) for s in self.spots)

		self.parse(problem)

	# Crosses two lists
	def crossLists(self, A, B):
		return [(a, b) for a in A for b in B]

	# The change here is that instead of giving a full range(1, 10) for every empty spot I just consider the spots around it
	# and eliminate those constraints from options around it. The data structure self.domains is still maintained as originally
	# intended in that self.domains still has every spot in self.spots as key and the value is a list that stores the possible values
	# that you can put in that spot. Professor confirmed on Slack that this change could be made.
	def parse(self, problem):
		s = Solver(self)
		for i in range(0, 9):
			for j in range(0, 9):
				c = problem[i*9+j] 
				if c != '.': # If a non empty spot is found then remove all those dependent values except for the value at that spot
					vals = s.assign(self.domains, (i+1, j+1), ord(c)-48)
					if not vals:
						return False
					else:
						self.domains = vals

	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				d = self.domains[(i+1,j+1)]
				if len(d) == 1:
					print(d[0], end='')
				else: 
					print('.', end='')
				if j == 2 or j == 5:
					print(" | ", end='')
			print()
			if i == 2 or i == 5:
				print("---------------")

class Solver:
	def __init__(self, grid):
		#sigma is the assignment function
		self.sigma = {}
		self.grid = grid
		# Stores values as the domains for the grid
		self.values = self.grid.domains

	def solve(self):
		# Get vals from searching through the grid
		vals = self.search(self.values)
		if not vals:
			return False
		# Update the domains of the grid to be the vals received from the search
		self.grid.domains = vals
		return vals

	# Run the backtracking search algorithm as described in the post
	def search(self, values):
		# Returned False before
		if values is False:
			return False
		# Search is done
		if all(len(values[s]) == 1 for s in self.grid.spots):
			return values
		# Choose the spot that has the minimum number of spots available
		n,s = min((len(values[s]), s) for s in self.grid.spots if len(values[s]) > 1)
		for d in values[s]:
			result = self.search(self.assign(copy.deepcopy(values), s, d))
			if result: return result

	# Remove s from values
	def replace(self, values, s):
		values = list(values)
		for i in range(0, len(values)):
			if(values[i] == s):
				values.pop(i)
				break
		return values
	
	# Eliminate all values from s except d, if there is a contradiction then return False
	def assign(self, values, s, d):
		other_values = values[s]
		other_values = self.replace(values[s], d)
		if(all(self.eliminate(values, s, d2) for d2 in other_values)):
			return values
		else:
			return False
	
	# Eliminate one of the possible values for a square
	def eliminate(self, values, s, d):
		if d not in list(values[s]): # Already eliminated
			return values
		values[s] = self.replace(values[s], d)
		if len(values[s]) == 0: # Contradiction: removed last value
			return False
		elif len(values[s]) == 1: # If only value then eliminate from peers
			if(len(values[s]) == 1):
				d2 = values[s][0]
			else:
				d2 = values[s]
			if not all(self.eliminate(values, s2, d2) for s2 in self.grid.peers[s]):
				return False
		
		# If only place for value d then put it there
		for u in self.grid.units[s]:
			dplaces = [s for s in u if d in values[s]]
			if len(dplaces) == 0: # Contradiction: put it there
				return False
			elif len(dplaces) == 1: # d can only be in one place in unit put it there
				if not self.assign(values, dplaces[0], d):
					return False
		return values

easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
"2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
"52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Problem====")
g = Grid(hard[0])
#Display the original problem
g.display()
s = Solver(g)
if s.solve():
	print("====Solution===")
	#Display the solution
	#Feel free to call other functions to display
	g.display()
else:
	print("==No solution==")