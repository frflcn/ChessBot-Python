from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ChessBoard import ChessBoard, Square, Move
# from ChessBoard import ChessBoard, Square
import ChessBoard
print(f'In Pieces {type(ChessBoard.Move)}')
from Colors import Color, Black, White, NoColor
import copy
class Piece:
    def __init__(self, color: Color, square: Square, board: ChessBoard = None):
        self.color = color
        if (isinstance(color, NoColor)):
            self.is_black = False
            self.is_white = False
            self.is_piece = False
        else:
            self.is_black = isinstance(color, Black)
            self.is_white = not self.is_black
            self.is_piece = True
        self.board = board
        self.square = square
        if (board != None):
            self.board.add_piece(self)
            if color == White():
                self.player = self.board.white
            elif color == Black():
                self.player = self.board.black
    def __str__(self):
        return str(self.color) + " " + str(type(self)) + " on " + str(self.square.file) + str(self.square.rank)
    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None = None) -> List[List[int]]:
        raise NotImplementedError("Do not call func: attack_squares_seen_int, on base class: Piece")
    def is_opposite_color(self, color: Color) -> bool:
        if (isinstance(color, NoColor)):
            return self.is_piece
        if isinstance(color, White):
            return self.is_black
        return self.is_white
    def is_color(self, color: Color) -> bool:
        if (isinstance(color, NoColor)):
            return not self.is_piece
        elif (isinstance(color, White)):
            return self.is_white
        return self.is_black
    def available_moves(self) -> tuple[List[Square], List[ChessBoard]]:
        raise NotImplementedError("Available moves not implemented on base class Piece")
                    
class NoPiece(Piece):
    points = 0
    def __init__(self, square, board = None):
        super().__init__(NoColor(), square, board)
        self.color = NoColor()




class King(Piece):
    points = 0
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None) -> List[List[int]]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        for rank in range(self.square._rank - 1, self.square._rank + 2):
            if rank < 0 or rank >= 8:
                continue
            for file in range(self.square._file - 1, self.square._file + 2):
                if file < 0 or file >= 8:
                    continue
                if self.board[file][rank].color == self.color:
                    continue
                #squares_seen.append(Square(file, rank))
                squares_seen[file][rank] += 1
        return squares_seen
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        for rank in range(self.square._rank - 1, self.square._rank + 2):
            if rank < 0 or rank >= 8:
                continue
            for file in range(self.square._file - 1, self.square._file + 2):
                if file < 0 or file >= 8:
                    continue
                if self.board[file][rank].color == self.color:
                    continue
                #squares_seen.append(Square(file, rank))
                squares_seen.append(self.board.squares[file][rank])
        return squares_seen
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_moves = []
        available_squares = []
        possible_end_squares = self.attack_squares_seen()
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            move = Move(self.square, square)
            board.make_move(move.to_long_move())
            if not board.check_check(self.color):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        if self.player.can_kingside_castle:
            if self.color == White():
                attacked_squares = self.board.black.get_attack_squares_arr_int()
                if not attacked_squares[5][0] and not attacked_squares[6][0]:
                    if not self.board[5][0].is_piece and not self.board[6][0].is_piece:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(6, 0))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(6, 0))
            if self.color == Black():
                attacked_squares = self.board.white.get_attack_squares_arr_int()
                if not attacked_squares[5][8] and not attacked_squares[6][8]:
                    if not self.board[5][8].is_piece and not self.board[6][8].is_piece:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(6, 8))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(6, 8))
        if self.player.can_queenside_castle:
            if self.color == White():
                attacked_squares = self.board.black.get_attack_squares_arr_int()
                if not attacked_squares[3][0] and not attacked_squares[2][0]:
                    if not self.board[3][0].is_piece and not self.board[2][0].is_piece and not self.board[1][0]:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(2, 0))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(2, 0))
            if self.color == Black():
                attacked_squares = self.board.white.get_attack_squares_arr_int()
                if not attacked_squares[3][8] and not attacked_squares[2][8]:
                    if not self.board[3][8].is_piece and not self.board[2][8].is_piece and not self.board[1][8]:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(2, 8))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(2, 8))
        return available_squares, available_moves, chessboards

            




class Pawn(Piece):
    points = 1
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
        self.is_first_move = True
    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None) -> List[List[int]]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        direction = -1
        if self.color == White():
            direction = 1
        if self.square._file + 1 < 8:
            if self.board[self.square._file + 1][self.square._rank + (direction)].is_opposite_color(self.color):
                squares_seen[self.square._file + 1][self.square._rank + (direction)] += 1
            if self.board.squares[self.square._file + 1][self.square._rank + (direction)] == self.board.enpassant_available:
                squares_seen[self.square._file + 1][self.square._rank + (direction)] += 1
        if self.square._file - 1 >= 0:
            if self.board[self.square._file - 1][self.square._rank + (direction)].is_opposite_color(self.color):
                squares_seen[self.square._file - 1][self.square._rank + (direction)] += 1
            if self.board.squares[self.square._file - 1][self.square._rank + (direction)] == self.board.enpassant_available:
                squares_seen[self.square._file - 1][self.square._rank + (direction)] += 1
        return squares_seen
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        direction = -1
        if self.color == White():
            direction = 1
        if self.square._file + 1 < 8:
            if self.board[self.square._file + 1][self.square._rank + (direction)].is_opposite_color(self.color):
                print("Kingside")
                squares_seen.append(self.board.squares[self.square._file + 1][self.square._rank + (direction)])
        if self.square._file - 1 >= 0:
            if self.board[self.square._file - 1][self.square._rank + (direction)].is_opposite_color(self.color):
                print("Queenside")
                squares_seen.append(self.board.squares[self.square._file - 1][self.square._rank + (direction)])
        if self.enpassant_kingside_allowed():
            squares_seen.append(self.board.squares[self.square._file + 1][self.square._rank + (direction)])
        if self.enpassant_queenside_allowed():
            squares_seen.append(self.board.squares[self.square._file - 1][self.square._rank + (direction)])
        return squares_seen
    def enpassant_kingside_allowed(self):
        """
        Get this value from the associated board
        """
        return False
    def enpassant_queenside_allowed(self):
        """
            Get this value from the associated board
        """
        return False
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_squares = []
        available_moves = []
        possible_end_squares = self.attack_squares_seen()
        if self.color == White() and not self.board[self.square._file][self.square._rank + 1].is_piece:
            if self.square._rank == 6:
                end_square = Square(self.square._file, self.square._rank + 1)
                move = Move(self.square, end_square, promotion_piece=Queen)
                board = copy.deepcopy(self.board)
                board.make_move(move.to_long_move())
                if not board.check_check(self.color):
                    available_squares.append(end_square)
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Rook)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Bishop)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Knight)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
            else:
                possible_end_squares.append(Square(self.square._file, self.square._rank + 1))
            if not self.board[self.square._file][self.square._rank + 2].is_piece:  
                possible_end_squares.append(Square(self.square._file, self.square._rank + 2))
        if self.color == Black() and not self.board[self.square._file][self.square._rank - 1].is_piece:
            if self.square._rank == 1:
                end_square = Square(self.square._file, self.square._rank - 1)
                move = Move(self.square, end_square, promotion_piece=Queen)
                board = copy.deepcopy(self.board)
                board.make_move(move.to_long_move())
                if not board.check_check(self.color):
                    available_squares.append(end_square)
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Rook)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Bishop)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
                    move = Move(self.square, end_square, promotion_piece=Knight)
                    board = copy.deepcopy(self.board)
                    board.make_move(move.to_long_move())
                    chessboards.append(board)
                    available_moves.append(move)
            else:
                possible_end_squares.append(Square(self.square._file, self.square._rank - 1))
            if not self.board[self.square._file][self.square._rank - 2].is_piece:
                possible_end_squares.append(Square(self.square._file, self.square._rank - 2))
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            board.make_move(Move(self.square, square).to_long_move())
            if not board.check_check(self.color):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards
        

        

class Rook(Piece):
    points = 5
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)

    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None) -> List[List[int]]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        for increment in range(7):
            if self.square._file + increment + 1 > 7:
                break
            piece: Piece = self.board[self.square._file + increment + 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        return squares_seen
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        for increment in range(7):
            if self.square._file + increment + 1 > 7:
                break
            piece: Piece = self.board[self.square._file + increment + 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        return squares_seen
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_moves = []
        available_squares = []
        possible_end_squares = self.attack_squares_seen()
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            move = Move(self.square, square)
            board.make_move(move.to_long_move())
            if not board.check_check(self.color()):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards

class Knight(Piece):
    points = 3
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None) -> List[List[int]]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        for rank_direction in [-1, 1]:
            for file_direction in [-1, 1]:
                for zig_or_zag in [(1, 2), (2, 1)]:
                    new_file = self.square._file + (zig_or_zag[0] * file_direction)
                    new_rank = self.square._rank + (zig_or_zag[1] * rank_direction)
                    if new_file > 7 or new_file < 0:
                        continue
                    if new_rank > 7 or new_rank < 0:
                        continue
                    if self.board[new_file][new_rank].is_color(self.color):
                        continue
                    squares_seen[new_file][new_rank] += 1
        return squares_seen
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        for rank_direction in [-1, 1]:
            for file_direction in [-1, 1]:
                for zig_or_zag in [(1, 2), (2, 1)]:
                    new_file = self.square._file + (zig_or_zag[0] * file_direction)
                    new_rank = self.square._rank + (zig_or_zag[1] * rank_direction)
                    if new_file > 7 or new_file < 0:
                        continue
                    if new_rank > 7 or new_rank < 0:
                        continue
                    if self.board[new_file][new_rank].is_color(self.color):
                        continue
                    squares_seen.append(self.board.squares[new_file][new_rank])
        return squares_seen
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_moves = []
        available_squares = []
        possible_end_squares = self.attack_squares_seen()
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            move = Move(self.square, square)
            board.make_move(move.to_long_move())
            if not board.check_check(self.color()):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards

class Queen(Piece):
    points = 9

    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen_int_arr(self, squares_seen: List[List[int]] | None) -> List[List[int]]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank + increment + 1 > 7:
                break
            piece: Piece = self.board[self.square._file + increment + 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file + increment + 1 > 7:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        return squares_seen
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file + increment + 1 > 7:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        return squares_seen
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_moves = []
        available_squares = []
        possible_end_squares = self.attack_squares_seen()
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            move = Move(self.square, square)
            board.make_move(move.to_long_move())
            if not board.check_check(self.color()):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards

class Bishop(Piece):
    points = 3

    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)

    def attack_squares_seen_int_arr(self, squares_seen: List[int] | None = None) -> List[int]:
        if not squares_seen:
            squares_seen = [[0 for rank in range(8)] for file in range(8)]
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank + increment + 1 > 7:
                break
            piece: Piece = self.board[self.square._file + increment + 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen[piece.square._file][piece.square._rank] += 1
                break
            squares_seen[piece.square._file][piece.square._rank] += 1
        return squares_seen
        
    def attack_squares_seen(self) -> List[Square]:
        squares_seen = []
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file + increment + 1 > 7 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file + increment + 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank - increment - 1 < 0:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank - increment - 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        for increment in range(7):
            if self.square._file - increment - 1 < 0 or self.square._rank + increment + 1 > 7:
                break
            piece = self.board[self.square._file - increment - 1][self.square._rank + increment + 1]
            if piece.is_color(self.color):
                break
            if piece.is_opposite_color(self.color):
                squares_seen.append(piece.square)
                break
            squares_seen.append(piece.square)
        return squares_seen
    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_moves = []
        available_squares = []
        possible_end_squares = self.attack_squares_seen()
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            move = Move(self.square, square)
            board.make_move(move.to_long_move())
            if not board.check_check(self.color()):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards