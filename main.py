from random import randint, gauss


def lawn_to_dict(lawn):
    """
    Convert list of strings to dictionary of lists, where keys are row indexes
    Also return max index for dict and max index for row (assuming rectangular lawn)
    """
    return {idx: [ch for ch in row] for idx, row in enumerate(lawn)}


def _shoot_line(lawn_dict):
    """
    All line shooters shoot
    """
    if not isinstance(lawn_dict, dict):
        return lawn_dict
    for idx, line in lawn_dict.items():
        shoot_power = 0  # Set current shooting power in line to 0
        for idx_line, tile in enumerate(line):
            if tile.isdigit():  # is it shooter?
                shoot_power += int(tile)  # Add to shooting power
            elif tile[0] == "Z":  # is it zombie?
                if int(tile[1:]) <= shoot_power:  # Can we kill it?
                    shoot_power -= int(tile[1:])
                    line[idx_line] = " "
                else:  # Zombie too strong
                    line[idx_line] = "Z" + str(int(tile[1:])-shoot_power)
                    shoot_power = 0
    return lawn_dict


def _shoot_diag(lawn_dict, lawn_cols, lawn_rows, shooter_pos: list):
    """
    S shooters shoot in all direction, until they hit zombie or reach end of lawn
    """
    if not isinstance(lawn_dict, dict):
        return lawn_dict
    # shoot up
    row, col = shooter_pos
    while row > 0 and col < lawn_cols:
        row -= 1
        col += 1
        if lawn_dict[row][col][0] == 'Z':
            lawn_dict[row][col] = 'Z'+str(int(lawn_dict[row][col][1:])-1)
            if lawn_dict[row][col] == 'Z0':
                lawn_dict[row][col] = ' '
            break
    # shoot down
    row, col = shooter_pos
    while row < lawn_rows and col < lawn_cols:
        row += 1
        col += 1
        if lawn_dict[row][col][0] == 'Z':
            lawn_dict[row][col] = 'Z'+str(int(lawn_dict[row][col][1:])-1)
            if lawn_dict[row][col] == 'Z0':
                lawn_dict[row][col] = ' '
            break
    # shoot forward
    row, col = shooter_pos
    while col < lawn_cols:
        col += 1
        if lawn_dict[row][col][0] == 'Z':
            lawn_dict[row][col] = 'Z'+str(int(lawn_dict[row][col][1:])-1)
            if lawn_dict[row][col] == 'Z0':
                lawn_dict[row][col] = ' '
            break
    return lawn_dict


def _get_shooter_pos(lawn_dict):
    """
    Find all S shooters and order them right to left, top to bottom.
    We will iterate over them in this order
    """
    if not isinstance(lawn_dict, dict):
        return []
    shooter_list = []
    for row_idx, row in lawn_dict.items():
        for col_idx, col in enumerate(row):
            if col == 'S':
                shooter_list.append([row_idx, col_idx])
    return sorted(shooter_list, key=lambda l: (-l[1], l[0]))


def _move_zombies(lawn_dict, lawn_cols, zombies, timer):
    """
    Move current zombies, and add zombies that should appear
    Check if zombies reached the 0th column --> GameOver, lawn is None, loop will break
    Check if there are still some zombies on lawn
    Check if more zombies will come --> If both true, we won, lawn is "win", loop will break
    """
    no_zombies = True
    if not isinstance(lawn_dict, dict):
        return lawn_dict
    for idx, line in lawn_dict.items():
        shoot_power = 0
        for idx_line, tile in enumerate(line):
            if tile[0] == "Z":  # is it zombie?
                no_zombies = False
                if idx_line == 0:
                    return None  # GameOver :(
                else:
                    line[idx_line-1] = tile
                    line[idx_line] = ' '

    end_of_zombies = True
    for zombie in zombies:
        if zombie[0] == timer:
            end_of_zombies = False
            lawn_dict[zombie[1]][lawn_cols] = "Z"+str(zombie[2])
        elif zombie[0] > timer:
            end_of_zombies = False
    if end_of_zombies and no_zombies:
        return "win"
    else:
        return lawn_dict


def plants_and_zombies(lawn_dict, zombies, lawn_rows, lawn_cols):
    """
    Main procedure, loops until lawn_dict is valid dict.
    When set to non-dict state end game and return timer or None if we won
    Uncomment print block for printing state after each iteration
    """
    timer = 0
    while lawn_dict is not None and lawn_dict is not "win":
        print("Time: ", timer)
        print_lawn(lawn_dict)
        input()
        lawn_dict = _move_zombies(lawn_dict, lawn_cols, zombies, timer)
        shooters = _get_shooter_pos(lawn_dict)
        lawn_dict = _shoot_line(lawn_dict)
        for shooter in shooters:  # All S shooters shoot in order
            lawn_dict = _shoot_diag(lawn_dict, lawn_cols, lawn_rows, shooter)
        timer += 1
    if lawn_dict == "win":
        return None
    else:
        return timer-1


def generate_zombies(power, max_row, min_power=1, max_power=10, prob_in_time=0.1):
    zombies = []
    time = 0
    while power > 0:
        zom_power = randint(min_power, min(max_power, power))
        zombies.append([time, randint(0, max_row), zom_power])
        power -= zom_power
        if gauss(0, 1) > prob_in_time:
            time += 1
    return zombies


def print_lawn(lawn_dict):
    for lawn_line in lawn_dict.values():
        print(lawn_line)


def place_shooters(lawn_dict, money):
    lin_shooter_cost = 1
    diag_shooter_cost = 2
    what_to_place = input("You have ${}. \n Do you want to do any changes? (Y)es, (N)o - 150% money: ".format(money)).upper()
    if what_to_place == 'N':
        return lawn_dict, int(money*1.5)
    while what_to_place != 'E':
        print("Current state")
        print_lawn(lawn_dict)
        what_to_place = input("What to place: (E)nd placing, (L)ine shooter - ${}, (D)iagonal shooter - ${}: ".format(
            lin_shooter_cost, diag_shooter_cost)).upper()
        if what_to_place == "L":
            place_row = int(input("In which row you want to place it: "))
            place_col = int(input("In which column you want to place it: "))
            strong = int(input("How strong should shooter be? (max {}) ".format(money)))
            if strong <= money:
                try:
                    if lawn_dict[place_row][place_col] == " ":
                        lawn_dict[place_row][place_col] = str(strong)
                    elif lawn_dict[place_row][place_col].isdigit():
                        lawn_dict[place_row][place_col] = str(int(lawn_dict[place_row][place_col])+strong)
                    money -= strong
                except (IndexError, KeyError):
                    print("Invalid index")
        elif what_to_place == "D":
            if money >= diag_shooter_cost:
                place_row = int(input("In which row you want to place it: "))
                place_col = int(input("In which column you want to place it: "))
                try:
                    lawn_dict[place_row][place_col] = "S"
                except (IndexError, KeyError):
                    print("Invalid index")
                money -= diag_shooter_cost
            else:
                print("Not enough $$$")
        elif what_to_place == "E":
            pass
        else:
            print("Invalid option")
    return lawn_dict, money


if __name__ == '__main__':
    lawn_rows = int(input("Lawn rows: "))
    lawn_cols = int(input("Lawn cols: "))
    lawn = [" "*lawn_cols]*lawn_rows
    lawn_dict = lawn_to_dict(lawn)
    zom_max_power = 10
    power = 100
    res = None
    money = 10
    while res is None:  # Play the game
        lawn_dict, money = place_shooters(lawn_dict, money)
        zombies = generate_zombies(power, lawn_rows-1, max_power=zom_max_power)
        res = plants_and_zombies(lawn_dict, zombies, lawn_rows-1, lawn_cols-1)
        money = money+power/20
        power += 40
    print("GameOver")
