import random
from constants import positions, mills, neighbors

hand_pieces = {"blue": 10, "orange": 10}

curr_player = "orange"
other_player = "blue"

# Create a dictionary with board positions as keys
board = {pos: None for pos in positions}

# Print the board to verify
# print(board)

def generate_moves(current_player):
    global board, hand_pieces
    if current_player == "blue":
        hand = "h1"
    elif current_player == "orange":
        hand = "h2"

    player_board_count = 0
    for pos in board:
        if board[pos] == current_player:
            player_board_count += 1
    #Moving pieces from the hand to the board
    moves = []
    #Moving a piece from the hand to the board
    if hand_pieces[current_player] > 0:
        for pos in board:
            if board[pos] == None:
                test_board = board.copy()
                test_board[pos] = current_player
                if mill_formed(current_player, pos, test_board):
                    for removal in valid_removals(other_player):
                        moves.append((hand, pos, removal))
                else:
                    moves.append((hand, pos, "r0"))

    #Moving pieces on the board
    for source in board:
        if board[source] == current_player:
            for target in board:
                if board[target] == None:
                    if (hand_pieces[current_player] + player_board_count) > 3 and target not in neighbors[source]:
                        continue
                    test_board = board.copy()
                    test_board[source] = None
                    test_board[target] = current_player
                    if mill_formed(current_player, target, test_board):
                        for removal in valid_removals(other_player):
                            moves.append((source, target, removal))
                    else:
                        moves.append((source, target, "r0"))

    return moves, len(moves)

def mill_formed(player, pos, board) -> bool:
    for mill in mills:
        if pos in mill:
            if board[mill[0]] == player and board[mill[1]] == player and board[mill[2]] == player:
                return True
    return False

def valid_removals(opponent):
    global board

    opp_positions = []
    for pos in board:
        if board[pos] == opponent:
            opp_positions.append(pos)
        
    opp_not_mill = []
    for pos in opp_positions:
        if not mill_formed(opponent, pos, board):
            opp_not_mill.append(pos)

    if len(opp_not_mill) == 0:
        return opp_positions
    return opp_not_mill

# board["f6"] = "blue"
# print(generate_moves(curr_player))


def list_to_command(move):
    return f"{move[0]} {move[1]} {move[2]}"

def main():
    # Read initial color/symbol
    global curr_player, other_player, board
    curr_player = input().strip()
    if curr_player == "blue":
        other_player = "orange"
    else:
        other_player = "blue"
    first_move = True

    while True:
        if curr_player == "blue":
            hand = "h1"
        elif curr_player == "orange":
            hand = "h2"
        try:
            # Do not wait for input on the first turn
            if first_move and curr_player == "blue":
                first_move = False
                # Your move logic here
                moves, num_moves = generate_moves(curr_player)
                random_move = random.choice(moves)
                # Send move to referee and update board
                print(list_to_command(random_move), flush=True)
                board[random_move[1]] = curr_player
                if random_move[0] == hand:
                    hand_pieces[curr_player] -= 1
                else:
                    board[random_move[0]] = None
                if random_move[2] != "r0":
                    board[random_move[2]] = None
                continue

            # Read opponent's move and update board
            game_input = input().strip().split()
            board[game_input[1]] = other_player
            if game_input[0] == "h1" or game_input[0] == "h2":
                hand_pieces[other_player] -= 1
            else:
                board[game_input[0]] = None
            if game_input[2] != "r0":
                board[game_input[2]] = None

            # Your move logic here
            moves, num_moves = generate_moves(curr_player)
            random_move = random.choice(moves)
            

            # Send move to referee and update board
            print(list_to_command(random_move), flush=True)
            board[random_move[1]] = curr_player
            if random_move[0] == hand:
                hand_pieces[curr_player] -= 1
            else:
                board[random_move[0]] = None
            if random_move[2] != "r0":
                board[random_move[2]] = None

        except EOFError:
            break

if __name__ == "__main__":
    main()