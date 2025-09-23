from collections import deque

def rabbit_leap():
    # Initial and goal states
    initial_state = tuple(['E', 'E', 'E', '_', 'W', 'W', 'W'])
    goal_state = tuple(['W', 'W', 'W', '_', 'E', 'E', 'E'])

    # BFS setup
    queue = deque([(initial_state, [])])  # state + path of moves
    visited = set([initial_state])

    def get_moves(state):
        """Generate all valid moves from the current state."""
        moves = []
        pos = state.index('_')  # find empty space
        for shift in [-1, -2, 1, 2]:
            new_pos = pos + shift
            if 0 <= new_pos < len(state):
                # Check movement rules
                if shift < 0 and state[new_pos] == 'E':  # E moves right -> must be on left of space
                    moves.append(new_pos)
                elif shift > 0 and state[new_pos] == 'W':  # W moves left -> must be on right of space
                    moves.append(new_pos)
        return moves

    # BFS loop
    while queue:
        current_state, path = queue.popleft()

        # Goal check
        if current_state == goal_state:
            return path + [current_state]

        # Explore moves
        for move in get_moves(current_state):
            new_state = list(current_state)
            space = current_state.index('_')
            # Swap rabbit with space
            new_state[space], new_state[move] = new_state[move], new_state[space]
            new_state = tuple(new_state)

            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [current_state]))

    return None 


solution = rabbit_leap()
if solution:
    print("Solution found in", len(solution)-1, "moves:")
    for step in solution:
        print("".join(step))
else:
    print("No solution.")
