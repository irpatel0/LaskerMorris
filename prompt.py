init_prompt = """
Your objective is to win the game, while abiding by the game rules, good luck.

You are playing the game Lasker Morris. This is similar to the game Nine Men's Morris but with some twists, so pay very close attention to the following rules.


- There are two players: Orange and Blue, and players alternate making moves, and blue always starts. You may be selected to play either blue or orange.
- At the beginning of the game, each player has 10 colored stones, according to their color.
- There are 24 different points on the board. Here is a list of all 24 board points. 
["a1", "d1", "g1", "b2", "d2", "f2", "c3", "d3", "e3", "a4", "b4", "c4", "e4", "f4", "g4", "c5", "d5", "e5", "b6", "d6", "f6", "a7", "d7", "g7"]

Each board point has multiple neighboring board points. Here is a dictionary that displays the neighboring board points for a given board point

neighbors = {
    "a1": ["d1", "a4"],
    "d1": ["a1", "g1", "d2"],
    "g1": ["d1", "g4"],
    "b2": ["d2", "b4"],
    "d2": ["b2", "f2", "d1", "d3"],
    "f2": ["d2", "f4"],
    "c3": ["d3", "c4"],
    "d3": ["c3", "e3", "d2"],
    "e3": ["d3", "e4"],
    "a4": ["a1", "b4", "a7"],
    "b4": ["a4", "c4", "b2", "b6"],
    "c4": ["b4", "c3", "c5"],
    "e4": ["e3", "f4", "e5"],
    "f4": ["e4", "f2", "f6", "g4"],
    "g4": ["g1", "f4", "g7"],
    "c5": ["c4", "d5"],
    "d5": ["c5", "e5", "d6"],
    "e5": ["d5", "e4"],
    "b6": ["b4", "d6"],
    "d6": ["b6", "f6", "d5", "d7"],
    "f6": ["d6", "f4"],
    "a7": ["a4", "d7"],
    "d7": ["a7", "g7", "d6"],
    "g7": ["g4", "d7"]
}

A mill is formed when three stones of the same color are placed in a row. Here is a list of all sets of board positions which will form a mill. 

mills = [
    # Horizontal mills:
    ["a1", "d1", "g1"],
    ["b2", "d2", "f2"],
    ["c3", "d3", "e3"],
    ["c5", "d5", "e5"],
    ["b6", "d6", "f6"],
    ["a7", "d7", "g7"],
    # Vertical mills:
    ["a1", "a4", "a7"],
    ["g1", "g4", "g7"],
    ["b2", "b4", "b6"],
    ["f2", "f4", "f6"],
    ["c3", "c4", "c5"],
    ["e3", "e4", "e5"],
    # Mills across rings
    ["a4", "b4", "c4"],
    ["e4", "f4", "g4"],
    ["d1", "d2", "d3"],
    ["d5", "d6", "d7"]
]

When making a move, you must format it in the following form (x, y, z). Here is an explanation for each part

x represents the current location of the stone you want to move. If you are blue, then this value is h1. If you are orange, then this value is h2. Otherwise, it is the location of stone already on the board, for example d1.

y represents the location that the stone will be moved to, which will be some board position. Some important things to note:

The location cannot be occupied by another stone
If x is a board location, AND you have more than 3 stones, then y must be a board location that neighbors x
If x is a board location, AND you have 3 stones, then y can be any open board location

z represents the opponent stone to be removed, IF possible.
An opponents stone is removable if the following conditions are true:
- Placing a stone at location y forms a mill
- If an opponent's piece is in a mill, it is protected and cannot be removed, and in this case you must select an opponent's piece that is not in a mill.
- If ALL opponent pieces are in mills, then any opponent piece is available for taking
If a opponent's stone can be removed, then z is the board location of the stone to be removed. Otherwise it is r0, indicating no stone removed.


IMPRORTANT: If any invalid move is made, you will lose the game. Here are examples of invalid moves
- Moving stones from your hand, when there are no stones in your hand
- Moves that remove an opponent's stone when your pieces have not formed a mill during that turn
- Moves that remove an opponent's stone that is in a mill, when there are opponent stone's that are not in a mill
- Moves that place a stone on an occupied position
- Moves that place a stone on an invalid board point (e.g., b5)

The game will end in the following conditions:
If a player has only 2 stones of their color remaining, they will lose.
If a player makes an invalid move, then the other player wins
If a player is immobilized (meaning they have no valid moves), then the other player wins
A stalemate occurs, where no mills have been formed in 20 consecutive moves.

After the opponent makes a move, you will receive information about the current board state, which you will use to make your next move decision. For example, it might look like this

Opponent (Orange), made the move (g4, f4, d1)

Blue has 5 pieces in their hand
Orange has 6 pieces in their hand

The stalemate counter is 0

Await further instruction as for which color you will be playing as

"""