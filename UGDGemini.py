#imports
from constants import positions, mills, neighbors
from prompt import init_prompt
from google import genai
from dotenv import load_dotenv
import os
import re

#Initialize Gemini Chat
#be sure to have the google-genai package installed:
#pip install -q -U google-genai
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat = client.chats.create(model="gemini-2.0-flash")
response = chat.send_message(init_prompt)

# Global variables for the game
board = {pos: None for pos in positions} # Create a dictionary with board positions as keys
hand_pieces = {"blue": 10, "orange": 10}
curr_player_positions = []
opp_player_positions = []
curr_player = "blue"
other_player = "orange"
opp_previous_move = None

#Stalemate detection
STALEMATE_THRESHOLD = 20
stalemate_counter = 0
opp_prev_pieces_remaining = 10
prev_pieces_remaining = 10

#Create time-limit variable and time tracker
TIME_LIMIT = 5
TIME_LIMIT_SAFETY = TIME_LIMIT - 0.25
Timer = None

#Utility function to evaluate the game state and determine if the game is over
def static_eval(board, pieces, curr_pos, opp_pos, counter, depth, logging):
    player_board_count = len(curr_pos)
    other_board_count = len(opp_pos)
    if (pieces[curr_player] + player_board_count) < 3:
        if logging:
            print(f"Game over, {curr_player} has less than 3 pieces!", flush=True)
            exit(0)
        else:
            return -1000 - depth, True
    elif move_possible(curr_player, pieces, board, curr_pos) == False:
        if logging:
            print(f"Game over, {curr_player} has no valid moves left!", flush=True)
            exit(0)
        else:
            return -1000 - depth, True
    elif (pieces[other_player] + other_board_count) < 3:
        if logging:
            print(f"Game over, {other_player} has less than 3 pieces!", flush=True)
            exit(0)
        else:
            return 1000 + depth, True
    elif move_possible(other_player, pieces, board, opp_pos) == False:
        if logging:
            print(f"Game over, {other_player} has no valid moves left!", flush=True)
            exit(0)
        else:
            return 1000 + depth, True
    elif counter >= STALEMATE_THRESHOLD:
        if logging:
            print(f"Draw game! Players have not taken pieces in the past {STALEMATE_THRESHOLD} moves!", flush=True)
            exit(0)
        else:
            return 0, True
    else:
        return 0, False

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

    #If all pieces are in mills, any piece canbe removed
    if len(opp_not_mill) == 0:        return opp_positions
    return opp_not_mill

#Turn a move list into a string the referee can understand
def list_to_command(move):
    return f"{move[0]} {move[1]} {move[2]}"

def parse_response(response):
    matches = re.findall(r"\([^()]*\)", response, flags=re.DOTALL)

    if matches:
        last_match = matches[-1][1:-1]
        move = tuple(p.strip() for p in last_match.split(','))
        return move
    else:
        # print("Gemini did not provide a move in the correct format")
        return None

#Prompt a move from Gemini, and update the board accordingly. Deliver the move to the referee
def move_update(hand, first_move):
    global stalemate_counter, opp_prev_pieces_remaining
    # Your move logic here
    if first_move:
        if curr_player == "blue":
            response = chat.send_message("You are playing as blue, make the first move!")
        if curr_player == "orange":
            response = chat.send_message(f"""You are playing as orange. 
                                    Your opponent has made the first move {opp_previous_move}.
                                    Blue has {hand_pieces["blue"]} pieces in their hand
                                    Orange has {hand_pieces["orange"]} pieces in their hand.
                                    The stalemate counter is {stalemate_counter}""")
    else:
        response = chat.send_message(f"""It is now your move. 
                Your opponent has made the move {opp_previous_move}.
                Blue has {hand_pieces["blue"]} pieces in their hand
                Orange has {hand_pieces["orange"]} pieces in their hand.
                The stalemate counter is {stalemate_counter}
                Your pieces are in the following positions {curr_player_positions}
                Your opponent's pieces are in the following positions {opp_player_positions}""")

    next_move = parse_response(response.text)
    
    #TODO: Implement validation of the AI, continues to try and remove opponent's stones without forming a mill
    # Ways to incorrectly make a move:
    # IMPRORTANT: If any invalid move is made, you will lose the game. Here are examples of invalid moves
    # Moving stones from your hand, when there are no stones in your hand
    # Moves that remove an opponent's stone when your pieces have not formed a mill during that turn
    # Moves that remove an opponent's stone that is in a mill, when there are opponent stone's that are not in a mill
    # Moves that place a stone on an occupied position
    # Moves that place a stone on an invalid board point (e.g., b5)
    valid_move = tuple(next_move)
    if valid_move not in generate_moves(other_player, hand_pieces, board, opp_player_positions, curr_player_positions):
        chat.send_message(f"You played an invalid move ({response})!")
        move_update(hand, first_move)
    
    
    # Update board with move
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
    if opp_prev_pieces_remaining == hand_pieces[other_player] + len(opp_player_positions):
        stalemate_counter += 1
    else:
        stalemate_counter = 0
        opp_prev_pieces_remaining = hand_pieces[other_player] + len(opp_player_positions)

    #Send move to referee
    print(list_to_command(next_move), flush=True)
    #Check if the game is over after making a move
    score, game_over = static_eval(board, hand_pieces, curr_player_positions, opp_player_positions, stalemate_counter, 0, True)
    

def main():
    # Read initial color/symbol
    global curr_player, other_player, board, stalemate_counter, prev_pieces_remaining, opp_previous_move
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
                # Your move logic here
                move_update(hand, first_move)
                first_move = False
                continue

            # Read opponent's move and update board
            read = input()
            opp_previous_move = read
            game_input = read.strip().split()
            
            validate_move = tuple(game_input)
            if validate_move not in generate_moves(other_player, hand_pieces, board, opp_player_positions, curr_player_positions):
                print(f"Opponent played an invalid move ({game_input})!", flush=True)
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
            if prev_pieces_remaining == hand_pieces[curr_player] + len(curr_player_positions):
                stalemate_counter += 1
            else:
                stalemate_counter = 0
                prev_pieces_remaining = hand_pieces[curr_player] + len(curr_player_positions)

            # Your move logic here
            #Check if the game is over after updating the board with opponent's move
            score, game_over = static_eval(board, hand_pieces, curr_player_positions, opp_player_positions, stalemate_counter, 0, True)
            move_update(hand, first_move)
            first_move = False

        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()

# Testing