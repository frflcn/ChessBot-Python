from typing import List
from Pieces import Piece, King
from Colors import White, Color

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