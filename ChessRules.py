from __future__ import annotations
import typing
from typing import List, Type
import platform
import random
import time
import copy
import warnings
from multiprocessing import Pool

seed = time.time_ns()
print(f'{seed = }')
random.seed(seed)

def make_best_move(chessboard: ChessBoard) -> tuple[Move, ChessBoard]:
    return chessboard.make_best_move_half_depth(False)

class ChessError(Exception):
    def __init__(self, message: str):
        super().__init__(message) 

class Move:
    def __init__(self, start_square: Square, end_square: Square, is_taking = False, is_check = False, is_checkmate = False, is_kingside_castle = False, is_queenside_castle = False, is_enpassant = False, promotion_piece: Type | None = None):
        self.is_taking = is_taking
        self.is_check = is_check
        self.is_checkmate = is_checkmate
        self.is_enpassant = is_enpassant
        self.is_queenside_castle = is_queenside_castle
        self.is_kingside_castle = is_kingside_castle
        self.start_square = start_square
        self.end_square = end_square
        self.promotion_piece = promotion_piece
    def to_long_move(self) -> str:
        promotion_string = ""
        if self.promotion_piece == Queen:
            promotion_string = "q"
        elif self.promotion_piece == Rook:
            promotion_string = "r"
        elif self.promotion_piece == Bishop:
            promotion_string = "b"
        elif self.promotion_piece == Knight:
            promotion_string = "n"
        return str(self.start_square.file) + str(self.start_square.rank) + str(self.end_square.file) + str(self.end_square.rank) +  promotion_string


class Square:
    squares = [[None for rank in range(8)] for file in range(8)]

    def __new__(cls, file: int, rank: int) -> Square:
        if not cls.squares[file][rank]:
            cls.squares[file][rank] = super(Square, cls).__new__(cls)
        return cls.squares[file][rank]
    def __deepcopy__(self, _memo):
        return self

    def __init__(self, file: int, rank: int):
        self._file = file
        self._rank = rank
        self.file = chr(file + ord('a'))
        self.rank = rank + 1
    @staticmethod
    def new_square(file: chr, rank: int):
        """
            Input: File letter a-h, rank 1-8
            Returns: New Square
        """
        return Square(ord(file.lower()) - ord('a'), rank - 1)

class ChessBoard:
    def __init__(self):
        self.white : Player = Player(color=White())
        self.black : Player = Player(color=Black())
        self.squares : List[List[Square]] = [[Square(file, rank) for rank in range(8)] for file in range(8)]
        self.board : List[List[Piece]] = [[NoPiece(self.squares[file][rank]) for rank in range(8)] for file in range(8)]
        self._is_enpassant_available: bool = False
        self._enpassant_available: Square | None = None
        self.player_to_move = self.white
        self.waiting_player = self.black
        self.half_moves = 0
        self.moves = 0
    @property
    def enpassant_available(self) -> Square | None:
        return self._enpassant_available
    @enpassant_available.setter
    def enpassant_available(self, square: Square) -> None:
        self._enpassant_available = square
    @property
    def is_enpassant_available(self) -> bool:
        if self._enpassant_available == None:
            return False
        else:
            return True
    def get_available_moves(self) -> List[Move]:
        raise NotImplementedError("Get Available Moves Has Not Been Implemented Yet")
    def add_piece(self, piece: Piece) -> None:
        self.board[piece.square._file][piece.square._rank] = piece
        if (piece.is_white):
            self.white.add_piece(piece)
        elif (piece.is_black):
            self.black.add_piece(piece)
    def remove_piece(self, piece: Piece) -> None:
        self.board[piece.square._file][piece.square._rank] = NoPiece()
        if piece.is_white:
            self.white.remove_piece(piece)
        elif piece.is_black:
            self.black.remove_piece(piece)
    def __getitem__(self, key) -> Piece:
        return self.board[key]
    def __setitem__(self, key, new_value: Piece) -> None:
        self.board[key] = new_value
    def get_square(self, file: chr, rank: str) -> Square:
        return self.squares[ord(file.lower()) - ord('a')][rank - 1]
    def get_rudimentary_eval(self) -> int:
        eval = 0
        for piece in self.white.pieces:
            eval += piece.points
        for piece in self.black.pieces:
            eval -= piece.points
        if self.check_check():
            available_moves, _ = self.get_moves()
            if not available_moves:
                if self.player_to_move.color == Black():
                    return float("inf")
                else:
                    return float("-inf")
        return eval
    def make_moves(self, moves: List[str]) -> None:
        for move in moves:
            self.make_move(move)
    def make_move(self, move: str, update: bool = True) -> None:
        piece: Piece = self.board[ord(move[0].lower()) - ord('a')][ord(move[1]) - ord('1')]
        if isinstance(piece, King):
            if move == "e1g1":
                self.make_move("h1f1", False)
            elif move == "e1c1":
                self.make_move("a1d1", False)
            elif move == "e8g8":
                self.make_move("h8f8", False)
            elif move == "e8c8":
                self.make_move("a8d8", False)
            if piece.is_black:
                self.black.can_kingside_castle = False
                self.black.can_queenside_castle = False
            else:
                self.white.can_kingside_castle = False
                self.white.can_queenside_castle = False
        if move[:2] == "h1":
            self.white.can_kingside_castle = False
        elif move[:2] == "h8":
            self.black.can_kingside_castle = False
        elif move[:2] == "a1":
            self.white.can_queenside_castle = False
        elif move[:2] == "a8":
            self.black.can_queenside_castle = False
        attacked_piece = self.board[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')]
        if attacked_piece.is_black:
            self.black.remove_piece(attacked_piece)
        elif attacked_piece.is_white:
            self.white.remove_piece(attacked_piece)
        NoPiece(self.squares[ord(move[0].lower()) - ord('a')][ord(move[1]) - ord('1')], self)
        self.board[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')] = piece
        piece.square = self.squares[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')]
        if isinstance(piece, Pawn):
            if piece.color == White():
                direction = -1
            else:
                direction = 1
            attacked_piece = self.board[piece.square._file][int(str(move[3])) + direction - 1]
            enpassant_square = self.squares[piece.square._file][piece.square._rank]
            if (self.enpassant_available == enpassant_square):
                if attacked_piece.is_black:
                    self.black.remove_piece(attacked_piece)
                else:
                    self.white.remove_piece(attacked_piece)
                NoPiece(attacked_piece.square, self)
            if (move[1] == '2' and move[3] == '4'):
                self._enpassant_available = Square.new_square(move[2], 3)
            elif (move[1] == '7' and move[3] == '5'):
                self._enpassant_available = Square.new_square(move[2], 6)
            else:
                self._enpassant_available = None
            if (piece.is_black and move[3] == '1') or (piece.is_white and move[3] == '8'):
                if piece.is_black:
                    self.black.remove_piece(piece)
                else:
                    self.white.remove_piece(piece)
                color = piece.color
                match move[4]:
                    case 'q':
                        Queen(color, piece.square, self)
                    case 'n':
                        Knight(color, piece.square, self)
                    case 'b':
                        Bishop(color, piece.square, self)
                    case 'r':
                        Rook(color, piece.square, self)
        else:
            self._enpassant_available = None
        if update:
            temp = self.player_to_move
            self.player_to_move = self.waiting_player
            self.waiting_player = temp
        
    def check_check(self, defendingSide: Color | None = None) -> bool:
        attackSquares = [[0 for rank in range(8)] for file in range(8)]
        attackingPlayer = self.waiting_player
        defendingPlayer = self.player_to_move

        if defendingSide == White():
            attackingPlayer = self.black
            defendingPlayer = self.white
        elif defendingSide == Black():
            attackingPlayer = self.white
            defendingPlayer = self.black

        for piece in attackingPlayer.pieces:
            attackSquares = piece.attack_squares_seen_int_arr(attackSquares)
        if attackSquares[defendingPlayer.king.square._file][defendingPlayer.king.square._rank]:
            return True
        return False


    @staticmethod
    def create_starting_board() -> ChessBoard:
        board = ChessBoard()

        King(Black(), board.squares[4][7], board)
        King(White(), board.squares[4][0], board)
        Queen(Black(), board.squares[3][7], board)
        Queen(White(), board.squares[3][0], board)
        Rook(Black(), board.squares[0][7], board)
        Rook(White(), board.squares[0][0], board)
        Rook(Black(), board.squares[7][7], board)
        Rook(White(), board.squares[7][0], board)
        Bishop(Black(), board.squares[2][7], board)
        Bishop(White(), board.squares[2][0], board)
        Bishop(Black(), board.squares[5][7], board)
        Bishop(White(), board.squares[5][0], board)
        Knight(Black(), board.squares[6][7], board)
        Knight(White(), board.squares[6][0], board)
        Knight(Black(), board.squares[1][7], board)
        Knight(White(), board.squares[1][0], board)
        Pawn(Black(), board.squares[7][6], board)
        Pawn(White(), board.squares[7][1], board)
        Pawn(Black(), board.squares[6][6], board)
        Pawn(White(), board.squares[6][1], board)
        Pawn(Black(), board.squares[5][6], board)
        Pawn(White(), board.squares[5][1], board)
        Pawn(Black(), board.squares[4][6], board)
        Pawn(White(), board.squares[4][1], board)
        Pawn(Black(), board.squares[3][6], board)
        Pawn(White(), board.squares[3][1], board)
        Pawn(Black(), board.squares[2][6], board)
        Pawn(White(), board.squares[2][1], board)
        Pawn(Black(), board.squares[1][6], board)
        Pawn(White(), board.squares[1][1], board)
        Pawn(Black(), board.squares[0][6], board)
        Pawn(White(), board.squares[0][1], board)
        return board
    def is_absolutely_pinned(self, piece: Piece) -> bool:
        warnings.warn("ChessBoard.is_absolutely_pinned has not been fully implemented")
    def get_moves(self) -> tuple[List[Move], List[ChessBoard]]:
        chessboards = []
        moves = []
        for piece in self.player_to_move.pieces:
            squares, pieceMoves, pieceChessboards = piece.available_moves()
            chessboards += pieceChessboards
            moves += pieceMoves
        return moves, chessboards
    def make_best_move_half_depth(self, halfdepth: int = 2, inplace: bool = True) -> tuple[Move, ChessBoard]:
        moves, chessboards = self.get_moves()
        evals = []
        best_moves = []
        best_chessboards = []
        if self.player_to_move.color == White():
            best_eval = float("-inf")
        else:
            best_eval = float("inf")

        for index in range(len(chessboards)):
            value = chessboards[index].make_best_move(False)
            if isinstance(value, Color):
                if isinstance(value, White):
                    eval = float("inf")
                elif isinstance(value, Black):
                    eval = float("-inf")
                else:
                    eval = 0
            else:
                nextmove, nextchessboard = value
                eval = nextchessboard.get_rudimentary_eval()
            if (self.player_to_move.color == White() and best_eval < eval) or (self.player_to_move.color == Black() and best_eval > eval):
                best_moves = [moves[index]]
                best_chessboards = [chessboards[index]]
                best_eval = eval
            elif best_eval == eval:
                best_moves.append(moves[index])
                best_chessboards.append(chessboards[index])

        index = random.randrange(len(best_chessboards))
        if inplace:
            self = best_chessboards[index]
        return best_moves[index], best_chessboards[index]
            



    def make_best_move(self, inplace: bool = True) -> tuple[Move, ChessBoard] | Color:
        moves, chessboards = self.get_moves()
        if len(moves) == 0:
            if self.check_check():
                if self.player_to_move.color == White():
                    return Black()
                else:
                    return White()
            else:
                return NoColor()
        best_moves = []
        best_chessboards = []
        if self.player_to_move.color == White():
            best_eval = float("-inf")
            for index in range(len(chessboards)):
                eval = chessboards[index].get_rudimentary_eval()
                if eval > best_eval:
                    best_eval = eval
                    best_moves = [moves[index]]
                    best_chessboards = [chessboards[index]]
                elif eval == best_eval:
                    best_moves.append(moves[index])
                    best_chessboards.append(chessboards[index])
        elif self.player_to_move.color == Black():
            best_eval = float("inf")
            for index in range(len(chessboards)):
                eval = chessboards[index].get_rudimentary_eval()
                if eval < best_eval:
                    best_eval = eval
                    best_moves = [moves[index]]
                    best_chessboards = [chessboards[index]]
                elif eval == best_eval:
                    best_moves.append(moves[index])
                    best_chessboards.append(chessboards[index])
        index = random.randrange(len(best_moves))
        if inplace:
            self = best_chessboards[index]
        return best_moves[index], best_chessboards[index]
    @staticmethod
    def from_fen(fen: str) -> ChessBoard:
        board = ChessBoard()
        rank = 7
        file = 0
        stringIndex = 0
        while True:
            if fen[stringIndex] == '/':
                stringIndex += 1
                continue
            elif fen[stringIndex] == 'k':
                King(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'q':
                Queen(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'r':
                Rook(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'b':
                Bishop(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'n':
                Knight(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'p':
                Pawn(Black(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'K':
                King(White(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'Q':
                Queen(White(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'R':
                Rook(White(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'B':
                Bishop(White(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'N':
                Knight(White(), board.squares[file][rank], board)
            elif fen[stringIndex] == 'P':
                Pawn(White(), board.squares[file][rank], board)
            if fen[stringIndex] <= '8' and fen[stringIndex] >= '1':
                file += int(fen[stringIndex])
            else:
                file += 1
            stringIndex += 1
            if file > 7:
                file = 0
                rank -= 1
                stringIndex += 1

            if rank == -1:
                break

        if fen[stringIndex] == 'w':
            board.player_to_move = board.white
            board.waiting_player = board.black
        elif fen[stringIndex] == 'b':
            board.player_to_move = board.black
            board.waiting_player = board.white
        else:
            raise ValueError("Invalid FEN")
        stringIndex += 2

        board.white.can_kingside_castle = False
        board.white.can_queenside_castle = False
        board.black.can_kingside_castle = False
        board.black.can_queenside_castle = False
        if fen[stringIndex] == '-':
            stringIndex += 1
        if fen[stringIndex] == 'K':
            board.white.can_kingside_castle = True
            stringIndex += 1
        if fen[stringIndex] == 'Q':
            board.white.can_queenside_castle = True
            stringIndex += 1
        if fen[stringIndex] == 'k':
            board.black.can_kingside_castle = True
            stringIndex += 1
        if fen[stringIndex] == 'q':
            board.black.can_queenside_castle = True
            stringIndex += 1
        stringIndex += 1

        if fen[stringIndex] == '-':
            stringIndex += 2
        else:
            board._enpassant_available = Square.new_square(fen[stringIndex], fen[stringIndex + 1])
            stringIndex += 3
            

        digits = []
        while fen[stringIndex] != ' ':
            digits.append(fen[stringIndex])
            stringIndex += 1
        board.half_moves = int("".join(digits))
        stringIndex += 1

        digits = []
        while stringIndex < len(fen):
            digits.append(fen[stringIndex])
            stringIndex += 1
        board.moves = int("".join(digits))
        stringIndex += 1

        return board

        

            
    @property
    def fen(self) -> str:
        fen = ""
        for rankIndex in range(7, -1, -1):
            noPieceCount = 0
            for fileIndex in range(8):
                piece: Piece = self.board[fileIndex][rankIndex]
                if isinstance(piece, NoPiece):
                    noPieceCount += 1
                elif isinstance(piece, King):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'k'
                    else:
                        fen += 'K'
                elif isinstance(piece, Queen):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'q'
                    else:
                        fen += 'Q'
                elif isinstance(piece, Bishop):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'b'
                    else:
                        fen += 'B'
                elif isinstance(piece, Rook):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'r'
                    else:
                        fen += 'R'
                elif isinstance(piece, Knight):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'n'
                    else:
                        fen += 'N'
                elif isinstance(piece, Pawn):
                    if noPieceCount != 0:
                        fen += chr(noPieceCount)
                        noPieceCount = 0
                    if piece.is_black:
                        fen += 'p'
                    else:
                        fen += 'P'
            if noPieceCount != 0:
                fen += str(noPieceCount)
                noPieceCount = 0
            fen += "/"
        fen = fen[:-1]
        if self.player_to_move.color == White():
            fen += " w"
        else:
            fen += " b"
        canCastle = False
        castleString = " "
        if self.white.can_kingside_castle:
            canCastle = True
            castleString += 'K'
        if self.white.can_queenside_castle:
            canCastle = True
            castleString += 'Q'
        if self.black.can_kingside_castle:
            canCastle = True
            castleString += 'k'
        if self.black.can_queenside_castle:
            canCastle = True
            castleString += 'q'
        if canCastle:
            fen += castleString
        else:
            fen += " -"
        if self.enpassant_available:
            fen += " " + self.enpassant_available.file + self.enpassant_available.rank
        else:
            fen += " -"
        fen += " " + chr(self.half_moves + ord('0')) + " " + chr(self.moves + ord('0'))
        return fen

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
                if not attacked_squares[5][7] and not attacked_squares[6][7]:
                    if not self.board[5][7].is_piece and not self.board[6][7].is_piece:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(6, 7))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(6, 7))
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
                if not attacked_squares[3][7] and not attacked_squares[2][7]:
                    if not self.board[3][7].is_piece and not self.board[2][7].is_piece and not self.board[1][7]:
                        board = copy.deepcopy(self.board)
                        move = Move(self.square, Square(2, 7))
                        board.make_move(move.to_long_move())
                        chessboards.append(board)
                        available_moves.append(move)
                        available_squares.append(Square(2, 7))
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
                squares_seen.append(self.board.squares[self.square._file + 1][self.square._rank + (direction)])
            if self.board.squares[self.square._file + 1][self.square._rank + (direction)] == self.board.enpassant_available:
                squares_seen.append(self.board.squares[self.square._file + 1][self.square._rank + (direction)])
        if self.square._file - 1 >= 0:
            if self.board[self.square._file - 1][self.square._rank + (direction)].is_opposite_color(self.color):
                squares_seen.append(self.board.squares[self.square._file - 1][self.square._rank + (direction)])
            if self.board.squares[self.square._file - 1][self.square._rank + (direction)] == self.board.enpassant_available:
                squares_seen.append(self.board.squares[self.square._file - 1][self.square._rank + (direction)])
        return squares_seen

    


    def available_moves(self) -> tuple[List[Square], List[Move], List[ChessBoard]]:
        chessboards = []
        available_squares = []
        available_moves = []
        possible_end_squares = self.attack_squares_seen()
        def handle_promotions(end_square):
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

        if self.color == White() and not self.board[self.square._file][self.square._rank + 1].is_piece:
            if self.square._rank == 6:
                end_square = Square(self.square._file, self.square._rank + 1)
                handle_promotions(end_square)
            else:
                possible_end_squares.append(Square(self.square._file, self.square._rank + 1))
            if self.square._rank == 1 and (not self.board[self.square._file][self.square._rank + 2].is_piece):  
                possible_end_squares.append(Square(self.square._file, self.square._rank + 2))
        if self.color == Black() and not self.board[self.square._file][self.square._rank - 1].is_piece:
            if self.square._rank == 1:
                end_square = Square(self.square._file, self.square._rank - 1)
                handle_promotions(end_square)
            else:
                possible_end_squares.append(Square(self.square._file, self.square._rank - 1))
            if self.square._rank == 6 and (not self.board[self.square._file][self.square._rank - 2].is_piece):
                possible_end_squares.append(Square(self.square._file, self.square._rank - 2))
        for square in possible_end_squares:
            board = copy.deepcopy(self.board)
            if (self.is_white and square.rank == 8) or (self.is_black and square.rank == 1):
                handle_promotions(square)
            else:
                move = Move(self.square, square)
                board.make_move(move.to_long_move())
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
            if not board.check_check(self.color):
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
            if not board.check_check(self.color):
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
            if not board.check_check(self.color):
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
            if not board.check_check(self.color):
                chessboards.append(board)
                available_moves.append(move)
                available_squares.append(square)
        return available_squares, available_moves, chessboards
    
class Color:
    def __init__(self, is_white = True, is_black = False, is_piece = True):
        self.is_white = is_white
        self.is_black = is_black
        self.is_piece = is_piece
    def __str__(self):
        raise NotImplementedError("Base color class does not have string representation")

class Black(Color):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Black, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        super().__init__(False, True)
    def __str__(self):
        return "black"

class White(Color):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(White, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        super().__init__(True, False)
    def __str__(self):
        return "white"

class NoColor(Color):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NoColor, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        super().__init__(False, False, False)
    def __str__(self):
        return "Not a Color"
    
class Player:
    def __init__(self, pieces: List[Piece] = None, color: Color = White()):
        if pieces == None:
            pieces = []
        self.pieces = pieces
        self.can_queenside_castle = True
        self.can_kingside_castle = True
        self._is_in_check = False
        self._is_in_doublecheck = False
        self._is_checkmated = False
        self._is_in_bishop_check = False
        self._is_in_knight_check = False
        self._is_in_rook_check = False
        self.color = color
        self.king = None
    def get_attack_squares_arr_int(self) -> List[List[int]]:
        attack_squares = [[0 for rank in range(8)] for file in range(8)]
        for piece in self.pieces:
            attack_squares = piece.attack_squares_seen_int_arr(attack_squares)
        return attack_squares
    @property
    def is_in_check(self) -> bool:
        return self._is_in_check
    @is_in_check.setter
    def is_in_check(self, value: bool) -> None:
        if not value:
            self._is_checkmated = False
            self._is_in_doublecheck = False
            self._is_in_knight_check = False
            self._is_in_rook_check = False
            self._is_in_bishop_check = False
        self._is_in_check = value
    @property
    def is_in_doublecheck(self) -> bool:
        return self._is_in_doublecheck
    @is_in_doublecheck.setter
    def is_in_doublecheck(self, value: bool) -> None:
        if value:
            self._is_in_check = True
        self._is_in_doublecheck = value
    @property
    def is_checkmated(self) -> bool:
        return self._is_checkmated
    @is_checkmated.setter
    def is_checkmated(self, value: bool) -> None:
        if value:
            self._is_in_check = True
        self._is_checkmated = value
    @property
    def is_in_bishop_check(self) -> bool:
        return self._is_in_bishop_check
    @is_in_bishop_check.setter
    def is_in_bishop_check(self, value: bool) -> None:
        if value:
            self._is_in_check = True
        self._is_in_bishop_check = value
    @property
    def is_in_rook_check(self) -> bool:
        return self._is_in_rook_check
    @is_in_rook_check.setter
    def is_in_rook_check(self, value: bool) -> None:
        if value:
            self._is_in_check = True
        self._is_in_rook_check = value
    @property
    def is_in_knight_check(self) -> bool:
        return self._is_in_knight_check
    @is_in_knight_check.setter
    def is_in_knight_check(self, value: bool) -> None:
        if value:
            self._is_in_check = True
        self._is_in_knight_check = value
    def add_piece(self, piece: Piece) -> None:
        self.pieces.append(piece)
        if isinstance(piece, King):
            self.king = piece
    def remove_piece(self, piece) -> None:
        self.pieces.remove(piece)