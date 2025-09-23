import heapq
from copy import deepcopy

# --------------------------
# Board Representation
# --------------------------
# Standard English Solitaire board (7x7 cross, invalid = -1)
initial_board = [
    [-1, -1, 1, 1, 1, -1, -1],
    [-1, -1, 1, 1, 1, -1, -1],
    [ 1,  1, 1, 1, 1,  1,  1],
    [ 1,  1, 1, 0, 1,  1,  1],  # center empty
    [ 1,  1, 1, 1, 1,  1,  1],
    [-1, -1, 1, 1, 1, -1, -1],
    [-1, -1, 1, 1, 1, -1, -1]
]

GOAL = (3, 3)  # center

# Convert board to tuple of tuples (hashable)
def to_tuple(board):
    return tuple(tuple(row) for row in board)

# Pretty print
def print_board(board):
    for row in board:
        print(" ".join("." if cell == 0 else "#" if cell == 1 else " " for cell in row))
    print()

# --------------------------
# Move Generation
# --------------------------
DIRECTIONS = [(0,1),(0,-1),(1,0),(-1,0)]  # right, left, down, up

def valid_moves(board):
    moves = []
    for r in range(7):
        for c in range(7):
            if board[r][c] == 1:  # marble
                for dr, dc in DIRECTIONS:
                    r1, c1 = r+dr, c+dc
                    r2, c2 = r+2*dr, c+2*dc
                    if 0 <= r2 < 7 and 0 <= c2 < 7:
                        if board[r1][c1] == 1 and board[r2][c2] == 0:
                            moves.append(((r, c), (r2, c2)))
    return moves

def apply_move(board, move):
    """Apply a move on a board (works with tuple states)."""
    (r, c), (r2, c2) = move
    dr, dc = (r2-r)//2, (c2-c)//2

    # Convert to list of lists so we can modify
    new_board = [list(row) for row in board]

    new_board[r][c] = 0
    new_board[r+dr][c+dc] = 0
    new_board[r2][c2] = 1

    return new_board

# --------------------------
# Heuristic Functions
# --------------------------
def heuristic_marble_count(board):
    """h1: Number of marbles left (lower is better)."""
    return sum(cell==1 for row in board for cell in row)

def heuristic_distance_to_center(board):
    """h2: Sum of Manhattan distances of marbles to center."""
    r_goal, c_goal = GOAL
    dist = 0
    for r in range(7):
        for c in range(7):
            if board[r][c] == 1:
                dist += abs(r-r_goal) + abs(c-c_goal)
    return dist

# --------------------------
# Search Algorithms
# --------------------------
def search(initial_board, heuristic=None, use_path_cost=True):
    """Generic best-first / UCS / A* search."""
    frontier = []
    start = to_tuple(initial_board)
    heapq.heappush(frontier, (0, 0, start, []))  # (priority, g, state, path)
    explored = set()

    while frontier:
        f, g, state, path = heapq.heappop(frontier)

        if state in explored:
            continue
        explored.add(state)

        # Goal test: one marble in the center only
        marble_count = sum(cell==1 for row in state for cell in row)
        if marble_count == 1 and state[GOAL[0]][GOAL[1]] == 1:
            return path, g, len(explored)

        # Expand neighbors
        moves = valid_moves(state)
        for move in moves:
            new_board = apply_move(state, move)
            new_state = to_tuple(new_board)
            new_g = g + 1
            h = heuristic(new_board) if heuristic else 0
            f_score = 0
            if use_path_cost and heuristic:
                f_score = new_g + h     # A*
            elif use_path_cost:
                f_score = new_g         # UCS
            elif heuristic:
                f_score = h             # Greedy Best-First
            else:
                f_score = new_g

            heapq.heappush(frontier, (f_score, new_g, new_state, path+[move]))

    return None, None, len(explored)

# --------------------------
# Run and Compare
# --------------------------
if __name__ == "__main__":
    print("Initial Board:")
    print_board(initial_board)

    print("Running Uniform Cost Search...")
    path, cost, expanded = search(initial_board, heuristic=None, use_path_cost=True)
    print(" UCS -> cost:", cost, "expanded:", expanded)

    print("\nRunning Best-First Search (h1 = marble count)...")
    path, cost, expanded = search(initial_board, heuristic=heuristic_marble_count, use_path_cost=False)
    print(" Best-First (h1) -> cost:", cost, "expanded:", expanded)

    print("\nRunning Best-First Search (h2 = distance to center)...")
    path, cost, expanded = search(initial_board, heuristic=heuristic_distance_to_center, use_path_cost=False)
    print(" Best-First (h2) -> cost:", cost, "expanded:", expanded)

    print("\nRunning A* Search (h1)...")
    path, cost, expanded = search(initial_board, heuristic=heuristic_marble_count, use_path_cost=True)
    print(" A* (h1) -> cost:", cost, "expanded:", expanded)

    print("\nRunning A* Search (h2)...")
    path, cost, expanded = search(initial_board, heuristic=heuristic_distance_to_center, use_path_cost=True)
    print(" A* (h2) -> cost:", cost, "expanded:", expanded)

    # Optional: print one solution step by step
    if path:
        print("\nSolution (step by step):")
        board = initial_board
        print_board(board)
        for move in path:
            board = apply_move(board, move)
            print_board(board)
