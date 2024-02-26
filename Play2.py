#By Cburnett - Own work, CC BY-SA 3.0, https://commons.wikimedia.org/w/index.php?curid=1499810
import pygame 
from pygame import Rect, Surface, Color, image
import io
from ChessRules import ChessBoard, Pawn, Rook, Bishop, Knight, King, Queen, NoPiece, Piece
# from ChessBoard import ChessBoard
# from Pieces import Pawn, Rook, Bishop, Knight, King, Queen, NoPiece, Piece
from stockfish import Stockfish
import math
import chess
import chess.engine

def load_and_scale_svg(filename, scale):
    svg_string = open(filename, "rt").read()
    start = svg_string.find('<svg')    
    if start > 0:
        svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]
    start = svg_string.find('width="')
    end = svg_string[start+7:].find('"')
    width = int(svg_string[start+7:start+7+end])
    if start > 0:
        svg_string = svg_string[:start+7] + f'{scale * width}"' + svg_string[start+7+end:]
    start = svg_string.find('height="')
    end = svg_string[start+8:].find('"')
    height = int(svg_string[start+8:start+8+end])
    if start > 0:
        svg_string = svg_string[:start+8] + f'{scale * height}"' + svg_string[start+8+end:]


    return pygame.image.load(io.BytesIO(svg_string.encode()))




# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

chess_board = ChessBoard.create_starting_board()


print(f'{chess_board.check_check() = }')

engine = chess.engine.SimpleEngine.popen_uci("C:\\Program Files\\komodo-14\\komodo")
engine.configure({"Skill" : 0})
board: chess.Board = chess.Board()
#print (dir(engine))

stockfish = Stockfish(path="C:\\Program Files\\Stockfish\\stockfish")
stockfish.set_position()

stockfish.update_engine_parameters({"UCI_LimitStrength" : True})

stockfish.update_engine_parameters({"Skill Level" : 0})
stockfish.update_engine_parameters({"UCI_Elo" : 100})
stockfish.update_engine_parameters({"MultiPV" : 5})

fen = "3b4/3r4/1n1p4/pr1kn3/p5p1/q7/b4K2/3q4 w - - 1 85"
chess_board = ChessBoard.from_fen(fen)
stockfish.set_fen_position(fen)

size_of_squares = 45

dark_square = Surface((size_of_squares, size_of_squares))
light_square = Surface((size_of_squares, size_of_squares))
dark_square.fill(Color(100, 100, 100))
light_square.fill(Color(180, 180, 180))

black_pawn = load_and_scale_svg(".\\Images\\black_pawn.svg", size_of_squares / 45)
black_king = load_and_scale_svg(".\\Images\\black_king.svg", size_of_squares / 45)
black_queen = load_and_scale_svg(".\\Images\\black_queen.svg", size_of_squares / 45)
black_rook = load_and_scale_svg(".\\Images\\black_rook.svg", size_of_squares / 45)
black_bishop = load_and_scale_svg(".\\Images\\black_bishop.svg", size_of_squares / 45)
black_knight = load_and_scale_svg(".\\Images\\black_knight.svg", size_of_squares / 45)
white_pawn = load_and_scale_svg(".\\Images\\white_pawn.svg", size_of_squares / 45)
white_king = load_and_scale_svg(".\\Images\\white_king.svg", size_of_squares / 45)
white_queen = load_and_scale_svg(".\\Images\\white_queen.svg", size_of_squares / 45)
white_rook = load_and_scale_svg(".\\Images\\white_rook.svg", size_of_squares / 45)
white_bishop = load_and_scale_svg(".\\Images\\white_bishop.svg", size_of_squares / 45)
white_knight = load_and_scale_svg(".\\Images\\white_knight.svg", size_of_squares / 45)

black_pawn = pygame.image.load(".\\Images\\black_pawn.svg")
black_king = pygame.image.load(".\\Images\\black_king.svg")
black_queen = pygame.image.load(".\\Images\\black_queen.svg")
black_rook = pygame.image.load(".\\Images\\black_rook.svg")
black_bishop = pygame.image.load(".\\Images\\black_bishop.svg")
black_knight = pygame.image.load(".\\Images\\black_knight.svg")
white_pawn = pygame.image.load(".\\Images\\white_pawn.svg")
white_king = pygame.image.load(".\\Images\\white_king.svg")
white_queen = pygame.image.load(".\\Images\\white_queen.svg")
white_rook = pygame.image.load(".\\Images\\white_rook.svg")
white_bishop = pygame.image.load(".\\Images\\white_bishop.svg")
white_knight = pygame.image.load(".\\Images\\white_knight.svg")

possible_move = Surface((size_of_squares, size_of_squares), pygame.SRCALPHA)
possible_move.fill(Color(255,255,255,0))
pygame.draw.circle(possible_move, Color(50, 50, 50, 125), (size_of_squares / 2, size_of_squares / 2), size_of_squares / 2.5)

is_piece_selected = False
piece_selected: Piece | None = None
is_showing_black_promotion = False
is_showing_white_promotion = False
move = ""




def show_black_promotion():
    screen.blit(black_queen, (size_of_squares * 8, 0))
    screen.blit(black_rook, (size_of_squares * 8, size_of_squares))
    screen.blit(black_bishop, (size_of_squares * 8, size_of_squares * 2))
    screen.blit(black_knight, (size_of_squares * 8, size_of_squares * 3))

def show_white_promotion():
    screen.blit(white_queen, (size_of_squares * 8, 0))
    screen.blit(white_rook, (size_of_squares * 8, size_of_squares))
    screen.blit(white_bishop, (size_of_squares * 8, size_of_squares * 2))
    screen.blit(white_knight, (size_of_squares * 8, size_of_squares * 3))

def make_move(move):
    global piece_selected
    global is_showing_black_promotion
    global is_showing_white_promotion
    global chess_board
    if stockfish.is_move_correct(move):
        #board.push(chess.Move.from_uci(move))
        stockfish.make_moves_from_current_position([move])

        chess_board.make_move(move)
        if board.is_game_over():
            outcome = board.outcome()
            if outcome.winner == chess.WHITE:
                font = pygame.font.Font('freesansbold.ttf', 32)
                text = font.render("You won!", True, "black", "white")
                screen.blit(text, (size_of_squares * 2, size_of_squares * 2))
            return True
        move = stockfish.get_best_move()

        draw()
        
        #result = engine.play(board, chess.engine.Limit(time = 10))
        move, chess_board = chess_board.make_best_move_half_depth()
        stockfish.make_moves_from_current_position([move.to_long_move()])
        #board.push(chess.Move(chess.Square()))
        #chess_board.make_move(result.move.uci())
        piece_selected = None
        is_showing_white_promotion = False
        is_showing_black_promotion = False
        return True
    else:
        piece_selected = None
        is_showing_white_promotion = False
        is_showing_black_promotion = False
        return False
    
def show_available_moves():
    #print(piece_selected)
    global piece_selected
    if piece_selected == None or isinstance(piece_selected, NoPiece):
        return  
    squares_seen, _, _ = piece_selected.available_moves()
    for square in squares_seen:
        screen.blit(possible_move, (square._file * size_of_squares, (size_of_squares * 7) - (square._rank * size_of_squares)))

def draw():
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE
    #Draw Squares
    for file in range(8):
        for rank in range(8):
            if (rank + file) % 2 == 0:
                screen.blit(light_square, ((size_of_squares * file), (size_of_squares * rank)))
            else:
                screen.blit(dark_square, ((size_of_squares * file), (size_of_squares * rank)))

    #Draw Pieces
    for file in range(8):
        for rank in range(8):
            x = (size_of_squares * file)
            y = (size_of_squares * 7) - (size_of_squares * rank)
            if isinstance(chess_board[file][rank], Pawn):
                if chess_board[file][rank].is_black:
                    screen.blit(black_pawn, (x, y))
                else:
                    screen.blit(white_pawn, (x, y))
            if isinstance(chess_board[file][rank], Queen):
                if chess_board[file][rank].is_black:
                    screen.blit(black_queen, (x, y))
                else:
                    screen.blit(white_queen, (x, y))
            if isinstance(chess_board[file][rank], King):
                if chess_board[file][rank].is_black:
                    screen.blit(black_king, (x, y))
                else:
                    screen.blit(white_king, (x, y))
            if isinstance(chess_board[file][rank], Rook):
                if chess_board[file][rank].is_black:
                    screen.blit(black_rook, (x, y))
                else:
                    screen.blit(white_rook, (x, y))
            if isinstance(chess_board[file][rank], Bishop):
                if chess_board[file][rank].is_black:
                    screen.blit(black_bishop, (x, y))
                else:
                    screen.blit(white_bishop, (x, y))
            if isinstance(chess_board[file][rank], Knight):
                if chess_board[file][rank].is_black:
                    screen.blit(black_knight, (x, y))
                else:
                    screen.blit(white_knight, (x, y))

    #Draw promotion choices
    if is_showing_black_promotion:
        show_black_promotion()
    elif is_showing_white_promotion:
        show_white_promotion()
                
    #Draw possible moves
    show_available_moves()



    # for file in range(8):
    #     screen.blit(black_pawn, (size_of_squares * file, size_of_squares))
    # for file in range(2):
    #     for rank in range(8):
    #         screen.blit(possible_move, ((size_of_squares * file), (size_of_squares * rank)))
            
    #screen.blit()

    # flip() the display to put your work on screen
    pygame.display.flip()


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f'mouse pos:  {event.__dict__["pos"]}')
            if event.__dict__["button"] != 1:
                continue
            if not event.__dict__["pos"][0] < size_of_squares * 8 and not event.__dict__["pos"][1] < size_of_squares * 8:
                continue
            file = math.floor(event.__dict__["pos"][0] / size_of_squares)
            rank = 8 - math.floor(event.__dict__["pos"][1] / size_of_squares) - 1
            if (is_showing_black_promotion or is_showing_white_promotion) and file == 8 and rank < 8 and rank > 3:
                match rank:
                    case 7:
                        move += 'q'
                        make_move(move)
                    case 6:
                        move += 'r'
                        make_move(move)
                    case 5:
                        move += 'b'
                        make_move(move)
                    case 4:
                        move += 'n'
                        make_move(move)
                is_showing_black_promotion == False
                is_showing_white_promotion == False
            elif file < 8 and file >= 0 and rank < 8 and rank >= 0:
                if (isinstance(piece_selected, NoPiece) or piece_selected == None):
                    piece_selected = chess_board[file][rank]
                else:
                    move = piece_selected.square.file + chr(piece_selected.square.rank + ord('0')) + chr(file + ord('a')) + chr(rank + ord("1"))
                    if isinstance(piece_selected, Pawn):
                        if piece_selected.is_black and rank == 0:
                            is_showing_black_promotion = True
                        elif piece_selected.is_white and rank == 7:
                            is_showing_white_promotion = True
                        else:
                            print(stockfish.get_board_visual())
                            print(f'Is move correct: {stockfish.is_move_correct(move)}')
                            print(f'move: {move}')
                            if stockfish.is_move_correct(move):
                                make_move(move)
                            else:
                                move = ""
                                piece_selected = chess_board[file][rank]
                    else:
                        if stockfish.is_move_correct(move):
                            make_move(move)
                        else:
                            move = ""
                            piece_selected = chess_board[file][rank]
                
                

                

    draw()
    # # fill the screen with a color to wipe away anything from last frame
    # screen.fill("purple")

    # # RENDER YOUR GAME HERE
    # #Draw Squares
    # for file in range(8):
    #     for rank in range(8):
    #         if (rank + file) % 2 == 0:
    #             screen.blit(light_square, ((size_of_squares * file), (size_of_squares * rank)))
    #         else:
    #             screen.blit(dark_square, ((size_of_squares * file), (size_of_squares * rank)))

    # #Draw Pieces
    # for file in range(8):
    #     for rank in range(8):
    #         x = (size_of_squares * file)
    #         y = (size_of_squares * 7) - (size_of_squares * rank)
    #         if isinstance(chess_board[file][rank], Pawn):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_pawn, (x, y))
    #             else:
    #                 screen.blit(white_pawn, (x, y))
    #         if isinstance(chess_board[file][rank], Queen):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_queen, (x, y))
    #             else:
    #                 screen.blit(white_queen, (x, y))
    #         if isinstance(chess_board[file][rank], King):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_king, (x, y))
    #             else:
    #                 screen.blit(white_king, (x, y))
    #         if isinstance(chess_board[file][rank], Rook):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_rook, (x, y))
    #             else:
    #                 screen.blit(white_rook, (x, y))
    #         if isinstance(chess_board[file][rank], Bishop):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_bishop, (x, y))
    #             else:
    #                 screen.blit(white_bishop, (x, y))
    #         if isinstance(chess_board[file][rank], Knight):
    #             if chess_board[file][rank].is_black:
    #                 screen.blit(black_knight, (x, y))
    #             else:
    #                 screen.blit(white_knight, (x, y))

    # #Draw promotion choices
    # if is_showing_black_promotion:
    #     show_black_promotion()
    # elif is_showing_white_promotion:
    #     show_white_promotion()
                
    # #Draw possible moves
    # show_available_moves()



    # # for file in range(8):
    # #     screen.blit(black_pawn, (size_of_squares * file, size_of_squares))
    # # for file in range(2):
    # #     for rank in range(8):
    # #         screen.blit(possible_move, ((size_of_squares * file), (size_of_squares * rank)))
            
    # #screen.blit()

    # # flip() the display to put your work on screen
    # pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
