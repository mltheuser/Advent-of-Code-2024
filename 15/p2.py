import os
import time

from PIL import ImageFont, ImageDraw
from PIL import Image


def solve_part_2(filename, debug=False):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Parse the original warehouse map
    original_warehouse = parse_warehouse_map(lines)

    # Scale up the warehouse map
    warehouse = scale_up_warehouse(original_warehouse)

    # Parse the moves (unchanged from part 1)
    moves = parse_move_sequence(lines, original_warehouse)

    # Find robot position
    robot_row, robot_col = find_robot_position(warehouse)

    # Simulate robot movement
    simulate_robot_movement_sequence(moves, robot_col, robot_row, warehouse, debug)

    # Calculate box GPS sum
    gps_sum = calculate_box_gps_sum_part2(warehouse)

    return gps_sum

def scale_up_warehouse(original_warehouse):
    scaled_warehouse = []
    for row in original_warehouse:
        new_row = []
        for cell in row:
            if cell == '#':
                new_row.extend(['#', '#'])
            elif cell == 'O':
                new_row.extend(['[', ']'])
            elif cell == '.':
                new_row.extend(['.', '.'])
            elif cell == '@':
                new_row.extend(['@', '.'])
        scaled_warehouse.append(new_row)
    return scaled_warehouse

def find_robot_position(warehouse):
    # Find the robot's initial position
    for i, row in enumerate(warehouse):
        if '@' in row:
            return i, row.index('@')
    return None, None

def calculate_box_gps_sum_part2(warehouse):
    # Calculate the GPS coordinates for each box
    gps_sum = 0
    for i, row in enumerate(warehouse):
        for j in range(len(row)):
            if row[j] == '[':
                # Found a box - GPS is based on distance from top and left edges
                gps = 100 * i + j
                gps_sum += gps
    return gps_sum

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

    if warehouse[next_row][next_col] in ['[', ']']:
        # Box - try to push it
        if try_push_boxes(next_row, next_col, dr, dc, warehouse):
            # Successfully pushed boxes, move robot
            warehouse[robot_row][robot_col] = '.'
            warehouse[next_row][next_col] = '@'
            return next_row, next_col

    # Default case - couldn't move
    return robot_row, robot_col

def try_push_boxes(start_row, start_col, dr, dc, warehouse):
    safe_pushes = []
    queue = [(start_row, start_col)]
    seen = set()

    while len(queue) > 0:
        position = queue.pop(0)

        if position in seen:
            continue

        seen.add(position)

        symbol_at_position = warehouse[position[0]][position[1]]

        # up or down
        if dr != 0:
            if symbol_at_position == "]":
                queue.append((position[0], position[1]-1))
            if symbol_at_position == "[":
                queue.append((position[0], position[1]+1))

        next_position = (position[0] + dr, position[1] + dc)

        symbol_at_next_position = warehouse[next_position[0]][next_position[1]]

        if symbol_at_next_position == "#":
            return False
        if symbol_at_next_position in ["[", "]"]:
            queue.append(next_position)

        safe_pushes.append((position, next_position))

    # apply movement
    for a, b in reversed(safe_pushes):
        warehouse[b[0]][b[1]] = warehouse[a[0]][a[1]]
        warehouse[a[0]][a[1]] = '.'

    return True

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

    print("\nLegend: @ = Robot, [] = Box, # = Wall, . = Empty space")
    print("Press Ctrl+C to exit animation")


def simulate_robot_movement_sequence(moves, robot_col, robot_row, warehouse, debug=False):
    # Define direction vectors
    directions = {
        '^': (-1, 0),
        'v': (1, 0),
        '<': (0, -1),
        '>': (0, 1)
    }

    # For GIF creation
    frames = []

    # Display initial state if debugging
    if debug:
        display_warehouse(warehouse, moves[0] if moves else None)
        frames.append(create_ascii_frame(warehouse, moves[0] if moves else None))
        time.sleep(0.5)

    # Simulate the robot's movement
    for i, move in enumerate(moves):
        dr, dc = directions[move]
        robot_row, robot_col = try_move_robot(robot_row, robot_col, dr, dc, warehouse)

        # Display the state after each move for debugging
        if debug:
            next_move = moves[i + 1] if i + 1 < len(moves) else None
            display_warehouse(warehouse, next_move)
            frames.append(create_ascii_frame(warehouse, next_move))
            time.sleep(0.3)

    # Save the frames as a GIF if requested
    if debug:
        gif_filename = "warehouse_animation.gif"

        frames[0].save(
            gif_filename,
            format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=300,  # 300ms per frame
            loop=0         # Loop forever
        )
        print(f"Animation saved as {gif_filename}")

    return robot_row, robot_col

def is_valid_position(row, col, warehouse):
    """Check if a position is within the warehouse boundaries"""
    return 0 <= row < len(warehouse) and 0 <= col < len(warehouse[0])

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

def parse_move_sequence(lines, warehouse):
    # Parse the move sequence
    moves_text = ''.join(lines[len(warehouse):])
    moves = ''.join(c for c in moves_text if c in '^v<>')
    return moves

def create_ascii_frame(warehouse, next_move=None, font_size=24, padding=20):
    """Create an image frame of the warehouse as ASCII art (like console output)"""
    # Try to get a monospace font for consistent character spacing
    try:
        font = ImageFont.truetype("/Library/Fonts/SourceCodePro-VariableFont_wght.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Character size in the monospace font (width is approximate)
    char_width = font_size * 0.6
    char_height = font_size * 1.2

    legend_text = "Legend: @ = Robot, [] = Box, # = Wall, . = Empty space"

    # Calculate dimensions
    warehouse_text = [''.join(row) for row in warehouse]
    max_line_len = max([len(line) for line in warehouse_text] + [len(legend_text)])

    # Add lines for legend and next move
    lines_count = len(warehouse) + 5  # Warehouse + empty line + legend + move + padding

    width = int(max_line_len * char_width) + 2 * padding
    height = int(lines_count * char_height) + 2 * padding

    # Create image with white background
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw warehouse as text
    y_pos = padding
    for row in warehouse_text:
        draw.text((padding, y_pos), row, fill=(255, 255, 255), font=font)
        y_pos += char_height

    # Add empty line
    y_pos += char_height

    # Add next move if available
    if next_move:
        move_text = f"Next move: {next_move}"
        draw.text((padding, y_pos), move_text, fill=(255, 255, 255), font=font)
    else:
        draw.text((padding, y_pos), "Final state", fill=(255, 255, 255), font=font)
    y_pos += char_height

    # Add legend
    draw.text((padding, y_pos), legend_text,
              fill=(255, 255, 255), font=font)

    return img

if __name__ == "__main__":
    assert solve_part_2('multi-box-example.txt', debug=True) == 618
    assert solve_part_2('example-small.txt') == 1751
    assert solve_part_2('example-big.txt') == 9021
    assert solve_part_2('p2-input.txt') == 1521635