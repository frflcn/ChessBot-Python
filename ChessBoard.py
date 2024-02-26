from __future__ import annotations
import copy
import warnings
from typing import List, Type
from Colors import White, Black, Color
from Player import Player
from Pieces import Piece, Pawn, NoPiece, King, Queen, Rook, Bishop, Knight

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
        for piece in self.white:
            eval += piece.points
        for piece in self.black:
            eval -= piece.points
        if self.check_check():
            if not self.get_moves():
                if self.player_to_move.color == Black():
                    return float("inf")
                else:
                    return float("-inf")
        return eval
    def make_move(self, move: str) -> None:
        piece: Piece = self.board[ord(move[0].lower()) - ord('a')][ord(move[1]) - ord('1')]
        if isinstance(piece, King):
            if move == "e1g1":
                self.make_move("h1f1")
            elif move == "e1c1":
                self.make_move("a1d1")
            elif move == "e8g8":
                self.make_move("h8f8")
            elif move == "e8c8":
                self.make_move("a8d8")
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
            self.black.can_kingside_castle = False
        attacked_piece = self.board[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')]
        if attacked_piece.is_black:
            self.black.remove_piece(attacked_piece)
        elif attacked_piece.is_white:
            self.white.remove_piece(attacked_piece)
        NoPiece(self.squares[ord(move[0].lower()) - ord('a')][ord(move[1]) - ord('1')], self)
        self.board[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')] = piece
        piece.square = self.squares[ord(move[2].lower()) - ord('a')][ord(move[3]) - ord('1')]
        print(f'piece: {piece}')
        if isinstance(piece, Pawn):
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
                print(f'move 4: {move[4]}')
                match move[4]:
                    case 'q':
                        print("made queen")
                        Queen(color, piece.square, self)
                    case 'n':
                        Knight(color, piece.square, self)
                    case 'b':
                        Bishop(color, piece.square, self)
                    case 'r':
                        Rook(color, piece.square, self)
        else:
            self._enpassant_available = None
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
    def make_best_move(self, inplace: bool = True) -> tuple[Move, ChessBoard]:
        moves, chessboards = self.get_moves()
        best_move = moves[0]
        best_chessboard = chessboards[0]
        if self.player_to_move.color == White():
            best_eval = float("-inf")
            for index in range(len(chessboards)):
                eval = chessboards[index].get_rudimentary_eval()
                if eval > best_eval:
                    best_eval = eval
                    best_move = moves[index]
                    best_chessboard = chessboards[index]
        elif self.player_to_move.color == Black():
            best_eval = float("inf")
            for index in range(len(chessboards)):
                eval = chessboards[index].get_rudimentary_eval()
                if eval < best_eval:
                    best_eval = eval
                    best_move = moves[index]
                    best_chessboard = chessboards[index]
        if inplace:
            self = best_chessboard
        return best_move, best_chessboard
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
    
if __name__ == "__main__":
    board = ChessBoard.create_starting_board()
    print(board.check_check())
    print(board.fen)
    print(f'{Move(Square(0,0), Square(0,7), promotion_piece=Queen).to_long_move() = }')