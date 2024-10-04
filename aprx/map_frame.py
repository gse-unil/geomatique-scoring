"""
Implementation of the MapFrame.
"""

from .map_view import MapView

class MapFrame:
    """
    A MapFrame is an element of the Layout showing a map.
    """
    def __init__(self, project: object, element_json: dict):
        self.project = project
        self.json = element_json

        # Find the map based on the uRI or the viewableObjectPath
        map_uri = self.json.get('uRI', False) or self.json['view']['viewableObjectPath']
        self.map = self.project.map_with_uri(map_uri)


    @property
    def map_view(self) -> MapView:
        """
        Returns the map view of this map frame.
        It contains the scale, x- and y-coordinates in the map frame CRS, as well as the height and
        width.
        """
        return MapView(self.json['view'])
