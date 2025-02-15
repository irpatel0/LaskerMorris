from constants import positions, mills, neighbors

hand_pieces = {"blue": 10, "orange": 10}

curr_player = "orange"
other_player = "blue"

# Create a dictionary with board positions as keys
board = {pos: None for pos in positions}

def minimax(board, pieces, depth, alpha, beta, maximizing):
    next_best = []
    score, game_over = static_eval(board, pieces, depth, False)
    if game_over:
        return score, next_best
    if depth == 0:
        return dynamic_eval(board, pieces, depth), next_best

    if maximizing:
        max_score = float('-inf')
        for move in generate_moves(curr_player, pieces, board):
            iterate_board = board.copy()
            iterate_pieces = pieces.copy()
            iterate_board[move[1]] = curr_player
            if move[0] == "h1" or move[0] == "h2":
                iterate_pieces[curr_player] -= 1
            else:
                iterate_board[move[0]] = None
            if move[2] != "r0":
                iterate_board[move[2]] = None
            score, local_best = minimax(iterate_board, iterate_pieces, depth-1, alpha, beta, False)
            if score > max_score:
                max_score = score
                next_best = move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_score, next_best
    else:
        min_score = float('inf')
        for move in generate_moves(other_player, pieces, board):
            iterate_board = board.copy()
            iterate_pieces = pieces.copy()
            iterate_board[move[1]] = other_player
            if move[0] == "h1" or move[0] == "h2":
                iterate_pieces[other_player] -= 1
            else:
                iterate_board[move[0]] = None
            if move[2] != "r0":
                iterate_board[move[2]] = None
            score, local_best = minimax(iterate_board, iterate_pieces, depth-1, alpha, beta, True)
            if score < min_score:
                min_score = score
                next_best = move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_score, next_best
    
def static_eval(board, pieces, depth, logging):
    player_board_count = 0
    other_board_count = 0
    for pos in board:
        if board[pos] == curr_player:
            player_board_count += 1
        if board[pos] == other_player:
            other_board_count += 1
    if (pieces[curr_player] + player_board_count) < 3:
        return -1000 - depth, True
    elif (pieces[other_player] + other_board_count) < 3:
        return 1000 + depth, True
    else:
        return 0, False

def dynamic_eval(board, pieces, depth):
    score = 0
    score += pieces[curr_player]
    score -= pieces[other_player]
    for pos in board:
        if mill_formed(curr_player, pos, board):
            score += 5
        if mill_formed(other_player, pos, board):
            score -= 5
        if board[pos] == curr_player:
            score += 1
        if board[pos] == other_player:
            score -= 1
    return score
        
def generate_moves(player, pieces, board):
    if player == "blue":
        hand = "h1"
        opponent = "orange"
    elif player == "orange":
        hand = "h2"
        opponent = "blue"

    player_board_count = 0
    for pos in board:
        if board[pos] == player:
            player_board_count += 1
    #Moving pieces from the hand to the board
    moves = []
    #Moving a piece from the hand to the board
    if pieces[player] > 0:
        for pos in board:
            if board[pos] == None:
                test_board = board.copy()
                test_board[pos] = player
                if mill_formed(player, pos, test_board):
                    for removal in valid_removals(opponent, board):
                        moves.append((hand, pos, removal))
                else:
                    moves.append((hand, pos, "r0"))

    #Moving pieces on the board
    for source in board:
        if board[source] == player:
            for target in board:
                if board[target] == None:
                    if (pieces[player] + player_board_count) > 3 and target not in neighbors[source]:
                        continue
                    test_board = board.copy()
                    test_board[source] = None
                    test_board[target] = player
                    if mill_formed(player, target, test_board):
                        for removal in valid_removals(opponent, board):
                            moves.append((source, target, removal))
                    else:
                        moves.append((source, target, "r0"))
    return moves

def mill_formed(player, pos, board) -> bool:
    for mill in mills:
        if pos in mill:
            if board[mill[0]] == player and board[mill[1]] == player and board[mill[2]] == player:
                return True
    return False

def valid_removals(opponent, board):

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


# board["c3"] = "orange"
# board["c4"] = "orange"
# board["c5"] = "orange"
# board["a4"] = "blue"
# board["b2"] = "blue"
# board["d2"] = "blue"
# board["f2"] = "blue"
# board["f4"] = "blue"
# board["d6"] = "blue"

# print(generate_moves(curr_player, hand_pieces, board))
# score, next_move = minimax(board, hand_pieces, 7, float('-inf'), float('inf'), True)
# print(score, next_move)

def list_to_command(move):
    return f"{move[0]} {move[1]} {move[2]}"

def move_update(hand):
    # Your move logic here
    score, next_move = minimax(board, hand_pieces, 4, float('-inf'), float('inf'), True)
    
    # Send move to referee and update board
    print(list_to_command(next_move), flush=True)
    board[next_move[1]] = curr_player
    if next_move[0] == hand:
        hand_pieces[curr_player] -= 1
    else:
        board[next_move[0]] = None
    if next_move[2] != "r0":
        board[next_move[2]] = None

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
                move_update(hand)
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
            move_update(hand)

        except EOFError:
            break

if __name__ == "__main__":
    main()