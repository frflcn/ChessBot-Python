from Square import Square
from Pieces import Queen, Rook, Bishop, Knight
from typing import Type

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
