"""
Implementation of the colors.
"""

class RGBA:
    """
    RGBA color.
    """
    def __init__(self, r, g, b, a=100):
        self.r, self.g, self.b = r, g, b
        self.a = a

    def __repr__(self):
        return f'<RGBA({self.r}, {self.g}, {self.b}, {self.a})'

    def is_equal(self, other):
        """
        Checks if two colors are the same.
        """
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
