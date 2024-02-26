from __future__ import annotations
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