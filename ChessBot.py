class ChessBoard:
    def __init__(self):
        self.white = Player()
        self.black = Player()
        self.squares = [[Square(file, rank) for rank in range(8)] for file in range(8)]
        self.board = [[NoPiece(self.squares[file][rank]) for rank in range(8)] for file in range(8)]
    def add_piece(self, piece):
        self.board[piece.square._file][piece.square._rank] = piece
        if (piece.is_white):
            self.white.add_piece(piece)
        else:
            self.black.add_piece(piece)
    def __getitem__(self, key):
        return self.board[key]
    def __setitem__(self, key, new_value):
        self.board[key] = new_value
    def get_square(self, file, rank):
        return self.squares[ord(file.lower()) - ord('a')][rank - 1]
        
class Square:
    def __init__(self, file, rank):
        self._file = file
        self._rank = rank
        self.file = chr(file + ord('a'))
        self.rank = rank + 1
    # def __init__(self, file, rank):
    #     self.rank = rank
    #     self.file = file
    #     self._file = ord(file.lower()) - ord('a')
    #     self._rank = rank - 1
    @staticmethod
    def new_square(file, rank):
        """
            Input: File letter a-h, rank 1-8
            Returns: New Square
        """
        return Square(ord(file.lower()) - ord('a'), rank - 1)


class Move:
    def __init__(self, start_square, end_square, is_taking = False, is_check = False, is_checkmate = False, is_kingside_castle = False, is_queenside_castle = False, is_enpassant = False):
        self.is_taking = is_taking
        self.is_check = is_check
        self.is_checkmate = is_checkmate
        self.is_enpassant = is_enpassant
        self.is_queenside_castle = is_queenside_castle
        self.is_kingside_castle = is_kingside_castle
        self.start_square = start_square
        self.end_square = end_square

class Piece:
    def __init__(self, color, square, board = None):
        if (color != None and color.lower() != "black" and color.lower() != "white"):
            raise ValueError("Only None, 'white' or 'black' accepted")
        self.color = color
        if (color == None):
            self.is_black = False
            self.is_white = False
            self.is_piece = False
        else:
            self.is_black = color.lower() == "black"
            self.is_white = color.lower() == "white"
            self.is_piece = True
        self.board = board
        self.square = square
        if (board != None):
            self.board.add_piece(self)
    def __str__(self):
        return self.color + " " + str(type(self)) + " on " + str(self.square.file) + str(self.square.rank)
        
    def is_opposite_color(self, color):
        if (color.lower() != "black" and color.lower() != "white"):
            raise ValueError("Only 'white' or 'black' accepted")
        if color == 'white':
            return self.is_black
        return self.is_white
    def is_color(self, color):
        if (color != None and color.lower() != "black" and color.lower() != "white"):
            raise ValueError("Only None, 'white' or 'black' accepted")
        if (color == None):
            return self.is_piece
        elif (color.lower() == "white"):
            return self.is_white
        return self.is_black
                    
class NoPiece(Piece):
    def __init__(self, square, board = None):
        super().__init__(None, square, board)
        self.color = "Not a piece"

class Player:
    def __init__(self, pieces = []):
        self.pieces = pieces
    def add_piece(self, piece):
        self.pieces.append(piece)


class King(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen(self):
        squares_seen = []
        for rank in range(self._rank - 1, self._rank + 2):
            if rank < 0 or rank >= 8:
                continue
            for file in range(self._file - 1, self._file + 2):
                if file < 0 or file >= 8:
                    continue
                if self.board[file][rank].color == self.color:
                    continue
                squares_seen.append(Square(file, rank))
        return squares_seen
    def available_moves(self):
        available_moves = []
        for rank in range(self._rank - 1, self._rank + 2):
            if rank < 0 or rank >= 8:
                continue
            for file in range(self._file - 1, self._file + 2):
                if file < 0 or file >= 8:
                    continue
                if self.board[file][rank].color == self.color:
                    continue
                move = Move()


class Pawn(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
        self.is_first_move = True
        self.enpassant_queenside_allowed = False
        self.enpassant_kingside_allowed = False
    def attack_squares_seen(self):
        squares_seen = []
        direction = -1
        if self.color == "white":
            direction = 1
        if self.square._file + 1 < 8:
            if self.board[self.square._file + 1][self.square._rank + (direction)].is_opposite_color(self.color):
                squares_seen.append(self.board[self.square._file + 1][self.square._rank + (direction)])
        if self.square._file - 1 >= 0:
            if self.board[self.square._file - 1][self.square._rank + (direction)].is_opposite_color(self.color):
                squares_seen.append(self.board[self.square._file - 1][self.square._rank + (direction)])
        if self.enpassant_kingside_allowed():
            squares_seen.append(self.board[self.square._file + 1][self.square._rank + (direction)])
        if self.enpassant_queenside_allowed():
            squares_seen.append(self.board[self.square._file - 1][self.square._rank + (direction)])
        return squares_seen
    def enpassant_kingside_allowed():
        """
            Get this value from the associated board
        """
        pass
    def enpassant_queenside_allowed():
        """
            Get this value from the associated board
        """
        pass
        

        

class Rook(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)

    def attack_squares_seen(self):
        squares_seen = []
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

class Knight(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen(self):
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

class Queen(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)
    def attack_squares_seen(self):
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

class Bishop(Piece):
    def __init__(self, color, square, board = None):
        super().__init__(color, square, board)

    def attack_squares_seen(self):
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
        

def create_starting_board():
    board = ChessBoard()
    # King("black", Square.new_square('e', 8), board)
    # King("white", Square.new_square('e', 1), board)
    # Queen("black", Square.new_square('d', 8), board)
    # Queen("white", Square.new_square('d', 1), board)
    # Rook("black", Square.new_square('a', 8), board)
    # Rook("white", Square.new_square('a', 1), board)
    # Rook("black", Square.new_square('h', 8), board)
    # Rook("white", Square.new_square('h', 1), board)
    # Bishop("black", Square.new_square('c', 8), board)
    # Bishop("white", Square.new_square('c', 1), board)
    # Bishop("black", Square.new_square('f', 8), board)
    # Bishop("white", Square.new_square('f', 1), board)
    # Knight("black", Square.new_square('g', 8), board)
    # Knight("white", Square.new_square('g', 1), board)
    # Knight("black", Square.new_square('b', 8), board)
    # Knight("white", Square.new_square('b', 1), board)
    # Pawn("black", Square.new_square('h', 7), board)
    # Pawn("white", Square.new_square('h', 2), board)
    # Pawn("black", Square.new_square('g', 7), board)
    # Pawn("white", Square.new_square('g', 2), board)
    # Pawn("black", Square.new_square('f', 7), board)
    # Pawn("white", Square.new_square('f', 2), board)
    # Pawn("black", Square.new_square('e', 7), board)
    # Pawn("white", Square.new_square('e', 2), board)
    # Pawn("black", Square.new_square('d', 7), board)
    # Pawn("white", Square.new_square('d', 2), board)
    # Pawn("black", Square.new_square('c', 7), board)
    # Pawn("white", Square.new_square('c', 2), board)
    # Pawn("black", Square.new_square('b', 7), board)
    # Pawn("white", Square.new_square('b', 2), board)
    # Pawn("black", Square.new_square('a', 7), board)
    # Pawn("white", Square.new_square('a', 2), board)

    King("black", board.squares[4][7], board)
    King("white", board.squares[4][0], board)
    Queen("black", board.squares[3][7], board)
    Queen("white", board.squares[3][0], board)
    Rook("black", board.squares[0][7], board)
    Rook("white", board.squares[0][0], board)
    Rook("black", board.squares[7][7], board)
    Rook("white", board.squares[7][0], board)
    Bishop("black", board.squares[2][7], board)
    Bishop("white", board.squares[2][0], board)
    Bishop("black", board.squares[5][7], board)
    Bishop("white", board.squares[5][0], board)
    Knight("black", board.squares[6][7], board)
    Knight("white", board.squares[6][0], board)
    Knight("black", board.squares[1][7], board)
    Knight("white", board.squares[1][0], board)
    Pawn("black", board.squares[7][6], board)
    Pawn("white", board.squares[7][1], board)
    Pawn("black", board.squares[6][6], board)
    Pawn("white", board.squares[6][1], board)
    Pawn("black", board.squares[5][6], board)
    Pawn("white", board.squares[5][1], board)
    Pawn("black", board.squares[4][6], board)
    Pawn("white", board.squares[4][1], board)
    Pawn("black", board.squares[3][6], board)
    Pawn("white", board.squares[3][1], board)
    Pawn("black", board.squares[2][6], board)
    Pawn("white", board.squares[2][1], board)
    Pawn("black", board.squares[1][6], board)
    Pawn("white", board.squares[1][1], board)
    Pawn("black", board.squares[0][6], board)
    Pawn("white", board.squares[0][1], board)
    return board

board = create_starting_board()

print(board[7][0])