"""
Implementation of a ProjectItem.
"""

import json
import os

from .layer import Layer


class ProjectItem:
    """
    A project item, i.e. an element of the catalog such as a map, a layout, toolbox, GDB, etc.
    """
    def __init__(self, project: object, item_id: str, item_type: str, name: str, properties: dict):
        self.project = project
        self.item_id = item_id
        self.item_type = item_type
        self.name = name
        self.properties = properties

        # Define some properties which might be None in some cases, or filled in later.
        self.catalog_path = None
        self.cim_path = None

        # Check if there is a catalog path defined. A catalog path can take three different types
        # of values: a name (e.g. "ArcGIS Colors"), a path (e.g. to a Toolbox file), or a CIMPATH
        # which is the path inside the project file.
        cat_path = self.properties.get('catalogPath', None)

        # If it is an internal path, extract it to a separate property.
        # If cat_path is defined but does not represent an internal path, store it in self.cat_path
        if cat_path is not None:
            if cat_path.startswith('CIMPATH='):
                self.cim_path = cat_path.split('=')[1]
            else:
                self.cat_path = cat_path

        # The cache, empty when starting
        self.cache = {}


    def __repr__(self):
        return f'<{self.item_type}: "{self.name}">'


    def load_json(self):
        """
        Loads the JSON file of the project item if there is any and puts it in the cache.
        If it has already been loaded once, it does nothing.
        """
        if self.cim_path is None or self.cache.get('json', None) is not None:
            return

        with open(os.path.join(self.project.tmp_dir, self.cim_path), 'r', encoding='utf-8') as f:
            self.cache['json'] = json.loads(f.read())


    def layers(self) -> list:
        """
        Returns the layers of the project item. If the project item cannot have layers, it just
        returns an empty list.
        """
        if self.cim_path is None:
            return []

        # Make sure the content of the project item file is loaded.
        self.load_json()

        # Try to get the layers from the JSON
        lyrs_json = self.cache['json'].get('layers', [])

        # Convert the layer reference to a Layer instance based on the path
        layers = []
        for lj in lyrs_json:
            if lj.startswith('CIMPATH='):
                lpath = lj.split('=')[1]
                layers.append(Layer(project=self.project, layer_path=lpath))

        return layers
