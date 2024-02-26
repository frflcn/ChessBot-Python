from stockfish import Stockfish

stockfish = Stockfish(path="C:\\Program Files\\Stockfish\\stockfish")

stockfish.set_position()

stockfish.update_engine_parameters({"UCI_LimitStrength" : True})
stockfish.update_engine_parameters({"Skill Level" : 1})
stockfish.update_engine_parameters({"UCI_Elo" : 100})
stockfish.update_engine_parameters({"MultiPV" : 5})


game_is_over = False


list_of_moves = []
def computer_make_move2():
    global list_of_moves
    move = stockfish.get_best_move()
    stockfish.make_moves_from_current_position([move])
    list_of_moves.append(move)
    print(stockfish.get_board_visual())
    print(move)
    print(stockfish.get_evaluation())

def computer_make_move():
    global list_of_moves
    move = stockfish.get_top_moves(1)
    stockfish.make_moves_from_current_position([move[0]["Move"]])
    list_of_moves.append(move[0]["Move"])
    print(stockfish.get_board_visual())
    print(move[0]["Move"])
    print(stockfish.get_evaluation())

def player_make_move():
    global list_of_moves
    is_valid_move = False
    while not is_valid_move:
        move = input("Make your move: ")
        if move == "undo":
            stockfish.set_position(list_of_moves[:-2])
            list_of_moves = list_of_moves[:-2]
            print (stockfish.get_board_visual())
            continue
        if stockfish.is_move_correct(move):
            is_valid_move = True
    
    
    stockfish.make_moves_from_current_position([move])
    list_of_moves.append(move)
    print(stockfish.get_board_visual())

    print (stockfish.get_evaluation())
    print (stockfish.get_fen_position())


print(stockfish.get_board_visual())
while(not game_is_over):
    player_make_move()
    computer_make_move2()

    

if eval["type"] == "mate" and (eval["value"] == -0):
        print ("Oof you lost")
if eval["type"] == "mate" and (eval["value"] == 0 or eval["value"] == -0):
        print ("You won!!!")


