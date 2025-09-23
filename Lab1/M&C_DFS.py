def is_valid(state):
    M_left, C_left, boat = state
    M_right = 3 - M_left
    C_right = 3 - C_left

    # No negative values
    if M_left < 0 or C_left < 0 or M_right < 0 or C_right < 0:
        return False

    # Missionaries must never be outnumbered by cannibals
    if (M_left > 0 and M_left < C_left) or (M_right > 0 and M_right < C_right):
        return False

    return True


def get_successors(state):
    """
    Generate all possible next states from the current state.
    Boat can carry 1 or 2 people (missionaries or cannibals).
    """
    M_left, C_left, boat = state
    successors = []

    # Possible moves: (M, C)
    moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

    for m, c in moves:
        if boat == 1:  # boat on left side → move people from left to right
            new_state = (M_left - m, C_left - c, 0)
        else:  # boat on right side → move people from right to left
            new_state = (M_left + m, C_left + c, 1)

        if is_valid(new_state):
            successors.append(new_state)

    return successors


def dfs_missionaries_cannibals(start_state, goal_state):
    stack = [(start_state, [start_state])]
    visited = set()

    while stack:
        current_state, path = stack.pop()

        if current_state == goal_state:
            return path

        if current_state not in visited:
            visited.add(current_state)

            for successor in get_successors(current_state):
                if successor not in visited:
                    stack.append((successor, path + [successor]))

    return "No solution found"


if __name__ == "__main__":
    start = (3, 3, 1)   # 3 missionaries, 3 cannibals, boat on left
    goal = (0, 0, 0)    # all on right side, boat on right

    solution = dfs_missionaries_cannibals(start, goal)
    print("Solution path:")
    print(solution)
