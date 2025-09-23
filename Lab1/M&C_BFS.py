from collections import deque
def is_valid(state):
    M_left, C_left, boat = state
    M_right, C_right = 3 - M_left, 3 - C_left

    # Check for invalid ranges
    if not (0 <= M_left <= 3 and 0 <= C_left <= 3):
        return False

    # Missionaries are not eaten on left bank
    if M_left > 0 and C_left > M_left:
        return False

    # Missionaries are not eaten on right bank
    if M_right > 0 and C_right > M_right:
        return False

    return True

def get_successors(state):
    M_left, C_left, boat = state
    successors = []
    moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]  # possible moves

    for M_move, C_move in moves:
        if boat == 0:  # Boat on left bank
            new_state = (M_left - M_move, C_left - C_move, 1)
        else:  # Boat on right bank
            new_state = (M_left + M_move, C_left + C_move, 0)

        if is_valid(new_state):
            successors.append(new_state)

    return successors

def bfs(start_state, goal_state):
    queue = deque()
    queue.append((start_state, [start_state]))
    visited = set()

    while queue:
        current_state, path = queue.popleft()

        if current_state == goal_state:
            return path

        if current_state not in visited:
            visited.add(current_state)

            for successor in get_successors(current_state):
                if successor not in visited:
                    queue.append((successor, path + [successor]))

    return None


if __name__ == "__main__":
    start = (3, 3, 0)  # 3 missionaries, 3 cannibals, boat on left
    goal = (0, 0, 1)   # all moved to right
    solution = bfs(start, goal)

    if solution:
        print("Solution found:")
        for step in solution:
            print(step)
    else:
        print("No solution found")
