"""
Implementation of a ArcGIS Pro project class.
"""

import json
import os
import shutil
import tempfile
from zipfile import ZipFile

from .map import Map
from .layout import Layout


class Project:
    """
    Representation of an ArcGIS Pro project file. To open a project file:
    proj = aprx.Project(project_path)

    The file needs to be closed at the end with:
    proj.close()
    """

    def __init__(self, project_path):
        """
        Opens an ArcGIS Pro project file.
        """
        # Keep the path around
        self.path = project_path

        # Create a temporary directory and extract the project file in the temp dir.
        self.tmp_dir = tempfile.mkdtemp(prefix='aprx_')

        # Unzip the project file.
        with ZipFile(self.path, 'r') as zip_ref:
            zip_ref.extractall(self.tmp_dir)

        # Prepare a cache variable to avoid loading multiple times the same data.
        self.cache = {}

        # Read the file with all project items (the elements in the catalog)
        with open(os.path.join(self.tmp_dir, 'GISProject.json'), 'r', encoding='utf-8') as f:
            self.json = json.loads(f.read())

        self.project_items = self.json.get('projectItems', [])


    @property
    def maps(self) -> list:
        """
        Returns all project items which are of item type "Map".
        """
        # If the maps have already been loaded once, return them.
        if self.cache.get('maps', None) is not None:
            return self.cache['maps']

        # Load the maps
        self.cache['maps'] = [
            Map(self, it) for it in self.project_items if it['itemType'] == 'Map'
        ]

        return self.cache['maps']


    def map_with_uri(self, uri) -> Map:
        """
        Returns a map based on its uRI.
        """
        map_lst = [m for m in self.maps if m.uri == uri]
        return map_lst[0] if len(map_lst) == 1 else None


    @property
    def layouts(self) -> list:
        """
        Returns all project items which ar of item type "Layout"
        """
        # If the maps have already been loaded once, return them.
        if self.cache.get('layouts', None) is not None:
            return self.cache['layouts']

        # Load the layouts
        self.cache['layouts'] = [
            Layout(self, it) for it in self.project_items if it['itemType'] == 'Layout'
        ]

        return self.cache['layouts']


    def close(self):
        """
        Closes the ArcGIS Pro project file.
        """
        # All we need to do is to remove the temporary directory with the unzipped content.
        shutil.rmtree(self.tmp_dir)
