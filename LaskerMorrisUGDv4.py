#imports
import time
from constants import positions, mills, neighbors

# Global variables for the game
board = {pos: None for pos in positions} # Create a dictionary with board positions as keys
hand_pieces = {"blue": 10, "orange": 10}
curr_player = ""
other_player = ""
curr_player_positions = []
opp_player_positions = []

#Create time-limit variable and time tracker
time_limit = 4.75
Timer = None

#Iterative deepening minimax algorithm
def iterative_deepening(board, pieces, curr_pos, opp_pos, limit = time_limit):
    global Timer
    #Set the time limit
    Timer = time.time() + limit
    #Keep track of the best move and score found so far
    best_move = []
    max_score = float('-inf')
    depth = 1

    #While time remains, call minimax with increasing depth, using past iteration as a backup
    while True:
        try:
            score, next_move = minimax(board, pieces, curr_pos, opp_pos, depth, float('-inf'), float('inf'), True)
            best_move = next_move
            max_score = score
        except Exception:
            break
        depth += 1
    return max_score, best_move

#Minimax algorithm with alpha-beta pruning
def minimax(board, pieces, curr_pos, opp_pos, depth, alpha, beta, maximizing):
    #Check if time limit has been reached
    if time.time() > Timer:
        raise Exception("Time limit reached")
    next_best = []
    score, game_over = static_eval(board, pieces, curr_pos, opp_pos, depth, False)
    if game_over:
        return score, next_best
    if depth == 0:
        return dynamic_eval(board, pieces, curr_pos, opp_pos, depth), next_best

    if maximizing:
        max_score = float('-inf')
        #Iterate through all possible moves
        for move in generate_moves(curr_player, pieces, board, curr_pos, opp_pos):
            #Create a copy of the game for possible move
            iterate_board = board.copy()
            iterate_pieces = pieces.copy()
            iterate_curr_pos = curr_pos.copy()
            iterate_opp_pos = opp_pos.copy()
            #Update the copied game with the possible move
            iterate_board[move[1]] = curr_player
            iterate_curr_pos.append(move[1])
            if move[0] in ("h1", "h2"):
                iterate_pieces[curr_player] -= 1
            else:
                iterate_board[move[0]] = None
                iterate_curr_pos.remove(move[0])
            if move[2] != "r0":
                iterate_board[move[2]] = None
                iterate_opp_pos.remove(move[2])
            #Recursively call minimax with the possible game
            score, local_best = minimax(iterate_board, iterate_pieces, iterate_curr_pos, iterate_opp_pos, depth-1, alpha, beta, False)
            #Track the best move and score found so far
            if score > max_score:
                max_score = score
                next_best = move
            #Update alpha for pruning
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_score, next_best
    else:
        min_score = float('inf')
        #Iterate through all possible moves
        for move in generate_moves(other_player, pieces, board, opp_pos, curr_pos):
            #Create a copy of the game for possible move
            iterate_board = board.copy()
            iterate_pieces = pieces.copy()
            iterate_curr_pos = curr_pos.copy()
            iterate_opp_pos = opp_pos.copy()
            #Update the copied game with the possible move
            iterate_board[move[1]] = other_player
            iterate_opp_pos.append(move[1])
            if move[0] in ("h1", "h2"):
                iterate_pieces[other_player] -= 1
            else:
                iterate_board[move[0]] = None
                iterate_opp_pos.remove(move[0])
            if move[2] != "r0":
                iterate_board[move[2]] = None
                iterate_curr_pos.remove(move[2])
            #Recursively call minimax with the possible game
            score, local_best = minimax(iterate_board, iterate_pieces, iterate_curr_pos, iterate_opp_pos, depth-1, alpha, beta, True)
            #Track the best move and score found so far
            if score < min_score:
                min_score = score
                next_best = move
            #Update beta for pruning
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_score, next_best

#Utility function to evaluate the game state and determine if the game is over
def static_eval(board, pieces, curr_pos, opp_pos, depth, logging):
    player_board_count = len(curr_pos)
    other_board_count = len(opp_pos)
    if (pieces[curr_player] + player_board_count) < 3:
        if logging:
            print(f"Game over, {curr_player} has less than 3 pieces", flush=True)
            exit(0)
        else:
            return -1000 - depth, True
    elif move_possible(curr_player, pieces, board, curr_pos) == False:
        if logging:
            print(f"Game over, {curr_player} has no valid moves left", flush=True)
            exit(0)
        else:
            return -1000 - depth, True
    elif (pieces[other_player] + other_board_count) < 3:
        if logging:
            print(f"Game over, {other_player} has less than 3 pieces", flush=True)
            exit(0)
        else:
            return 1000 + depth, True
    elif move_possible(other_player, pieces, board, opp_pos) == False:
        if logging:
            print(f"Game over, {other_player} has no valid moves left", flush=True)
            exit(0)
        else:
            return 1000 + depth, True
    else:
        return 0, False

#Evaluation function to determine the score of the game
def dynamic_eval(board, pieces, curr_pos, opp_pos, depth):
    score = 0
    score += pieces[curr_player] + len(curr_pos)
    score -= pieces[other_player] + len(opp_pos)
    for pos in curr_pos:
        if mill_formed(curr_player, pos, board):
            score += 5
    for pos in opp_pos:
        if mill_formed(other_player, pos, board):
            score -= 5
    return score

#Determine if any moves are possible for a player
#IMPORTANT: this function depends on perspective of the player
def move_possible(player, pieces, board, positions):
    player_board_count = len(positions)
    if (pieces[player] + player_board_count) <= 3 or pieces[player] > 0:
        return True
    for source in positions:
        for target in neighbors[source]:
            if board[target] == None:
                return True
    return False
        
#Generate a list of all possible moves for a player
#IMPORTANT: this function depends on perspective of the player
def generate_moves(player, pieces, board, curr_pos, opp_pos):
    moves = []

    if player == "blue":
        hand = "h1"
        opponent = "orange"
    elif player == "orange":
        hand = "h2"
        opponent = "blue"

    player_board_count = len(curr_pos)

    #Moving a piece from the hand to the board
    if pieces[player] > 0:
        for pos in board:
            if board[pos] == None:
                #Check if the placed piece forms a mill
                test_board = board.copy()
                test_board[pos] = player
                if mill_formed(player, pos, test_board):
                    #If a mill is formed, add all possible removals to the move list
                    for removal in valid_removals(opponent, test_board, opp_pos):
                        moves.append((hand, pos, removal))
                else:
                    #Otherwise, add the move with no removal
                    moves.append((hand, pos, "r0"))

    #Moving pieces on the board
    for source in curr_pos:
        for target in board:
            if board[target] == None:
                #If the player has less than 3 pieces, they can move to any empty space even if it is not a neighbor
                if (pieces[player] + player_board_count) > 3 and target not in neighbors[source]:
                    continue
                test_board = board.copy()
                test_board[source] = None
                test_board[target] = player
                if mill_formed(player, target, test_board):
                    #If a mill is formed, add all possible removals to the move list
                    for removal in valid_removals(opponent, test_board, opp_pos):
                        moves.append((source, target, removal))
                else:
                    #Otherwise, add the move with no removal
                    moves.append((source, target, "r0"))
    return moves

#Check if a mill is formed at a position
def mill_formed(player, pos, board) -> bool:
    for mill in mills:
        if pos in mill:
            if board[mill[0]] == player and board[mill[1]] == player and board[mill[2]] == player:
                return True
    return False

#Check all pieces a player can remove
def valid_removals(opponent, board, opp_positions):
    opp_not_mill = []
    for pos in opp_positions:
        if not mill_formed(opponent, pos, board):
            opp_not_mill.append(pos)

    #If all pieces are in mills, any piece can be removed
    if len(opp_not_mill) == 0:
        return opp_positions
    return opp_not_mill

#Turn a move list into a string the referee can understand
def list_to_command(move):
    return f"{move[0]} {move[1]} {move[2]}"

#Create a move with minimax, and update the board accordingly. Deliver the move to the referee
def move_update(hand):
    # Your move logic here
    score, next_move = iterative_deepening(board, hand_pieces, curr_player_positions, opp_player_positions)
    
    # Send move to referee and update board
    print(list_to_command(next_move), flush=True)
    board[next_move[1]] = curr_player
    curr_player_positions.append(next_move[1])
    if next_move[0] == hand:
        hand_pieces[curr_player] -= 1
    else:
        board[next_move[0]] = None
        curr_player_positions.remove(next_move[0])
    if next_move[2] != "r0":
        board[next_move[2]] = None
        opp_player_positions.remove(next_move[2])

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
            
            #Check if the game is over before reading from opponent
            score, game_over = static_eval(board, hand_pieces, curr_player_positions, opp_player_positions, 0, True)

            # Read opponent's move and update board
            game_input = input().strip().split()
            validate_move = tuple(game_input)
            if validate_move not in generate_moves(other_player, hand_pieces, board, opp_player_positions, curr_player_positions):
                print(f"Opponent played an invalid move ({game_input})", flush=True)
                exit(0)
            board[game_input[1]] = other_player
            opp_player_positions.append(game_input[1])
            if game_input[0] in ("h1", "h2"):
                hand_pieces[other_player] -= 1
            else:
                board[game_input[0]] = None
                opp_player_positions.remove(game_input[0])
            if game_input[2] != "r0":
                board[game_input[2]] = None
                curr_player_positions.remove(game_input[2])

            # Your move logic here
            #Check if the game is over after updating the board with opponent's move
            score, game_over = static_eval(board, hand_pieces, curr_player_positions, opp_player_positions, 0, True)
            move_update(hand)

        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()

#Testing
# print(generate_moves(other_player, hand_pieces, board, curr_player_positions, opp_player_positions))
# score, game_over = static_eval(board, hand_pieces, curr_player_positions, opp_player_positions, 0, True)
# score, next_move = iterative_deepening(board, hand_pieces, curr_player_positions, opp_player_positions)
# print(score, next_move)

#TODO: Add stalemate detection
#TODO: Improve heuristic
#TODO: Make eval function == utility function ???
#TODO: Choose nodes to not expand ??? (V5 proved that the time it takes to analyze node value is not worth it)