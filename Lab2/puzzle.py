import random
import time
import tracemalloc
from collections import deque

# Goal state for Puzzle-8
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# ---------------- Puzzle-8 Environment ----------------
def expand(state):
    """Return all valid successor states from current state."""
    moves = []
    idx = state.index(0)
    row, col = divmod(idx, 3)
    directions = {'Up': (-1,0), 'Down': (1,0), 'Left': (0,-1), 'Right': (0,1)}
    for dr, dc in directions.values():
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_state = state[:]
            new_idx = r * 3 + c
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            moves.append(new_state)
    return moves

def generate_puzzle_at_depth(d):
    """Generate a Puzzle-8 instance at given depth d from the goal state."""
    state = GOAL_STATE[:]
    for _ in range(d):
        state = random.choice(expand(state))
    return state

# ---------------- Graph Search Agent (Uniform Cost BFS) ----------------
def graph_search(initial_state, goal_state):
    """
    Implements BFS assuming uniform cost per move (UCS equivalent).
    Returns path from initial to goal and number of moves.
    """
    frontier = deque([initial_state])
    came_from = {tuple(initial_state): None}
    explored = set()

    while frontier:
        node = frontier.popleft()
        explored.add(tuple(node))

        if node == goal_state:
            # Backtrack to get the path
            path = []
            cur = tuple(node)
            while cur is not None:
                path.append(list(cur))
                cur = came_from[cur]
            return path[::-1]  # reverse to get start->goal

        for child in expand(node):
            tchild = tuple(child)
            if tchild not in explored and tchild not in came_from:
                frontier.append(child)
                came_from[tchild] = tuple(node)
    return None

# ---------------- Measure Memory and Time ----------------
def measure_instance(depth):
    """Generate a puzzle and measure memory, time, moves to solve it."""
    instance = generate_puzzle_at_depth(depth)
    tracemalloc.start()
    start_time = time.time()
    path = graph_search(instance, GOAL_STATE)
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "Depth": depth,
        "Memory_MB": round(peak / 1024 / 1024, 2),
        "Time_s": round(end_time - start_time, 4),
        "Moves": len(path)-1 if path else None
    }

# ---------------- Run Example ----------------
if __name__ == "__main__":
    depths = [6,8,10,13,15,17,20,25,40]  # Change or extend as needed
    print(f"{'Depth':<6} {'Memory (MB)':<12} {'Time (s)':<10} {'Moves'}")
    print("-"*40)
    for d in depths:
        result = measure_instance(d)
        print(f"{result['Depth']:<6} {result['Memory_MB']:<12} {result['Time_s']:<10} {result['Moves']}")
