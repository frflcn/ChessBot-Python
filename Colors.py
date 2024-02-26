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