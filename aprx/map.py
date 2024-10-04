"""
Implementation of a Map.
"""

import json
import os

from .layer import Layer


class Map:
    """
    A map as it appears in the catalog
    """
    def __init__(self, project: object, properties: dict):
        self.project = project
        self.item_id = properties['iD']
        self.name = properties['name']
        self.properties = properties

        # For a map, the catalog path is a CIMPATH which is the path to a JSON file inside the
        # project archive. It is used as uRI for other elements (e.g. in the layout)
        self.uri = self.properties.get('catalogPath', None)

        # Extract the CIMPATH and keep it around
        self.cim_path = self.uri.split('=')[1]

        # The cache, empty when starting
        self.cache = {}

        # Load the JSON file for the layer
        with open(os.path.join(self.project.tmp_dir, self.cim_path), 'r', encoding='utf-8') as f:
            self.json = json.loads(f.read())


    def __repr__(self):
        return f'<Map: "{self.name}">'


    @property
    def layers(self) -> list:
        """
        Returns the layers of the map
        """
        # Try to get the layers from the JSON
        lyrs_json = self.json.get('layers', [])

        # Convert the layer reference to a Layer instance based on the path
        layers = []
        for lj in lyrs_json:
            if lj.startswith('CIMPATH='):
                lpath = lj.split('=')[1]
                layers.append(Layer(project=self.project, layer_path=lpath))

        return layers
