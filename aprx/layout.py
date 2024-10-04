"""
Implementation of a Layout.
"""

import json
import os

from .map_frame import MapFrame


class Layout:
    """
    A layout as it appears in the catalog
    """
    def __init__(self, project: object, properties: dict):
        self.project = project
        self.item_id = properties['iD']
        self.name = properties['name']
        self.properties = properties

        # For a map, the catalog path is a CIMPATH which is the path to a JSON file inside the
        # project archive.
        self.uri = self.properties.get('catalogPath', None)

        # Extract the CIMPATH and keep it around
        self.cim_path = self.uri.split('=')[1]

        # The cache, empty when starting
        self.cache = {}

        # Load the JSON file for the layer
        with open(os.path.join(self.project.tmp_dir, self.cim_path), 'r', encoding='utf-8') as f:
            self.json = json.loads(f.read())


    def __repr__(self):
        return f'<Layout: "{self.name}">'


    @property
    def map_frames(self) -> list:
        """
        Returns the map frames of the layout, as a list of Map instances.
        """
        # Try to get the layers from the JSON
        elements = self.json.get('elements', [])

        # Return the Map instances
        map_frames = []
        for elem in elements:
            if elem['type'] == 'CIMMapFrame':
                map_frames.append(MapFrame(project=self.project, element_json=elem))

        return map_frames
