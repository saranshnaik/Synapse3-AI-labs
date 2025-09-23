def rabbit_leap():
    # Initial and goal states
    initial_state = ('E', 'E', 'E', '_', 'W', 'W', 'W')
    goal_state = ('W', 'W', 'W', '_', 'E', 'E', 'E')

    # DFS stack and visited set
    stack = [(initial_state, [initial_state])]  # store (state, path)
    visited = set([initial_state])

    while stack:
        current_state, path = stack.pop()

        # Goal check
        if current_state == goal_state:
            return path

        # Find valid moves
        for new_state in generate_moves(current_state):
            if new_state not in visited:
                visited.add(new_state)
                stack.append((new_state, path + [new_state]))

    return None  # No solution found


def generate_moves(state):
    """Generate all valid moves for rabbits."""
    moves = []
    state = list(state)
    empty_index = state.index('_')

    # Check left side moves (W rabbits moving left)
    if empty_index + 1 < len(state) and state[empty_index + 1] == 'W':
        new_state = state[:]
        new_state[empty_index], new_state[empty_index + 1] = new_state[empty_index + 1], new_state[empty_index]
        moves.append(tuple(new_state))

    if empty_index + 2 < len(state) and state[empty_index + 2] == 'W' and state[empty_index + 1] == 'E':
        new_state = state[:]
        new_state[empty_index], new_state[empty_index + 2] = new_state[empty_index + 2], new_state[empty_index]
        moves.append(tuple(new_state))

    # Check right side moves (E rabbits moving right)
    if empty_index - 1 >= 0 and state[empty_index - 1] == 'E':
        new_state = state[:]
        new_state[empty_index], new_state[empty_index - 1] = new_state[empty_index - 1], new_state[empty_index]
        moves.append(tuple(new_state))

    if empty_index - 2 >= 0 and state[empty_index - 2] == 'E' and state[empty_index - 1] == 'W':
        new_state = state[:]
        new_state[empty_index], new_state[empty_index - 2] = new_state[empty_index - 2], new_state[empty_index]
        moves.append(tuple(new_state))

    return moves


solution = rabbit_leap()
if solution:
    print("Solution found in", len(solution)-1, "moves:")
    for step in solution:
        print("".join(step))
else:
    print("No solution found.")
