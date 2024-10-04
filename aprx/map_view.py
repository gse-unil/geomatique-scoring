"""
Implementation of the MapView
"""

class MapView:
    """
    The map view defines the extent of a map as well as the scale.
    """
    def __init__(self, properties):
        self.json = properties
        cam = self.json['camera']
        self.x = cam['x']
        self.y = cam['y']
        self.scale = cam['scale']
        self.height = cam['viewportHeight']
        self.width = cam['viewportWidth']

    def is_equal(self, other: object, tolerance: dict = None) -> bool:
        """
        Compares two map views to see if they are equal based on x, y and scale.
        """
        tolerance = {} if tolerance is None else tolerance

        if abs(self.x - other.x) > tolerance.get('x', 0):
            return False

        if abs(self.y - other.y) > tolerance.get('y', 0):
            return False

        if abs(self.scale - other.scale) > tolerance.get('scale', 0):
            return False

        return True
