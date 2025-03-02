import os
import time


def solve(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    warehouse = parse_warehouse_map(lines)

    moves = parse_move_sequence(lines, warehouse)

    robot_col, robot_row = find_robot_position(warehouse)

    simulate_robot_movement_sequence(moves, robot_col, robot_row, warehouse)

    gps_sum = calculate_box_gps_sum(warehouse)

    return gps_sum


def calculate_box_gps_sum(warehouse):
    # Calculate the GPS coordinates for each box
    gps_sum = 0
    for i, row in enumerate(warehouse):
        for j, cell in enumerate(row):
            if cell == 'O':
                gps = 100 * i + j
                gps_sum += gps
    return gps_sum


def simulate_robot_movement_sequence(moves, robot_col, robot_row, warehouse, debug=True):
    # Define direction vectors
    directions = {
        '^': (-1, 0),
        'v': (1, 0),
        '<': (0, -1),
        '>': (0, 1)
    }

    # Display initial state if debugging
    if debug:
        display_warehouse(warehouse, moves[0])
        time.sleep(0.5)

    # Simulate the robot's movement
    for i, move in enumerate(moves):
        dr, dc = directions[move]
        robot_row, robot_col = try_move_robot(robot_row, robot_col, dr, dc, warehouse)

        # Display the state after each move for debugging
        if debug:
            display_warehouse(warehouse, moves[i + 1] if i + 1 < len(moves) else None)
            time.sleep(0.3)  # Adjust timing as needed

    return robot_row, robot_col


def display_warehouse(warehouse, next_move=None):
    """Display the current state of the warehouse in the console"""
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print the warehouse grid
    for row in warehouse:
        print(''.join(row))

    # Show next move if available
    if next_move:
        print(f"\nNext move: {next_move}")
    else:
        print("\nFinal state")

    print("\nLegend: @ = Robot, O = Box, # = Wall, . = Empty space")
    print("Press Ctrl+C to exit animation")


def try_move_robot(robot_row, robot_col, dr, dc, warehouse):
    """Attempt to move robot in the specified direction and return new position"""
    next_row, next_col = robot_row + dr, robot_col + dc

    # Check if the next position is valid
    if not is_valid_position(next_row, next_col, warehouse) or warehouse[next_row][next_col] == '#':
        # Can't move - hitting a wall
        return robot_row, robot_col

    if warehouse[next_row][next_col] == '.':
        # Empty space - move the robot
        warehouse[robot_row][robot_col] = '.'
        warehouse[next_row][next_col] = '@'
        return next_row, next_col

    if warehouse[next_row][next_col] == 'O':
        # Box - try to push it
        if try_push_boxes(next_row, next_col, dr, dc, warehouse):
            # Successfully pushed boxes, move robot
            warehouse[robot_row][robot_col] = '.'
            warehouse[next_row][next_col] = '@'
            return next_row, next_col

    # Default case - couldn't move
    return robot_row, robot_col


def try_push_boxes(start_row, start_col, dr, dc, warehouse):
    """Try to push boxes starting from the given position in the specified direction.
    Returns True if successful, False otherwise."""
    # Find all boxes in a row that need to be pushed
    boxes = []
    r, c = start_row, start_col

    # Collect all boxes in a line
    while is_valid_position(r, c, warehouse) and warehouse[r][c] == 'O':
        boxes.append((r, c))
        r += dr
        c += dc

    # Check if there's enough space to push all boxes
    if not is_valid_position(r, c, warehouse) or warehouse[r][c] == '#':
        return False  # Can't push boxes

    # Push all boxes (from furthest to closest)
    for r, c in reversed(boxes):
        warehouse[r][c] = '.'
        warehouse[r + dr][c + dc] = 'O'

    return True


def is_valid_position(row, col, warehouse):
    """Check if a position is within the warehouse boundaries"""
    return 0 <= row < len(warehouse) and 0 <= col < len(warehouse[0])


def find_robot_position(warehouse):
    # Find the robot's initial position
    robot_row, robot_col = None, None
    for i, row in enumerate(warehouse):
        if '@' in row:
            robot_col = row.index('@')
            robot_row = i
            break
    return robot_col, robot_row


def parse_move_sequence(lines, warehouse):
    # Parse the move sequence
    moves_text = ''.join(lines[len(warehouse):])
    moves = ''.join(c for c in moves_text if c in '^v<>')
    return moves


def parse_warehouse_map(lines):
    # Parse the warehouse map
    warehouse = []
    for line in lines:
        line = line.rstrip()
        if any(c in line for c in ['#', '@', 'O']):
            warehouse.append(list(line))
        else:
            break
    return warehouse


if __name__ == "__main__":
    assert solve('example-small.txt') == 2028
    assert solve('example-big.txt') == 10092
    assert solve('p1-input.txt') == 1527563
