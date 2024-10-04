"""
Implementation of a ArcGIS Pro project class.
"""

import json
import os
import shutil
import tempfile
from zipfile import ZipFile

from .project_item import ProjectItem


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

        # Prepare a cache variable for avoiding reading multiple times the same files.
        self.cache = {}


    @property
    def items(self):
        """
        Returns a list with all project items. These are the elements which are typically shown
        in the ArcGIS Pro catalog, i.e. all maps, layouts, toolboxes, etc.
        """
        # If the items are already in the cache, just return them.
        if self.cache.get('items', None) is not None:
            return self.cache['items']

        # If the project JSON file has not yet been loaded into the cache, do it now.
        if self.cache.get('proj', None) is None:
            items_fp = os.path.join(self.tmp_dir, 'GISProject.json')
            with open(items_fp, 'r', encoding='utf-8') as f:
                self.cache['proj'] = json.loads(f.read())

        # We can now transform the project items in the JSON representation into ProjectItem
        # instances.
        proj_items_json = self.cache['proj'].get('projectItems', [])
        proj_items = []
        for item in proj_items_json:
            proj_items.append(
                ProjectItem(
                    project=self,
                    item_id=item['iD'],
                    item_type=item['itemType'],
                    name=item['name'],
                    properties=item
                )
            )

        # Keep the items in the cache
        self.cache['items'] = proj_items

        return proj_items


    @property
    def maps(self):
        """
        Returns all project items which are of item type "Map".
        """
        return [it for it in self.items if it.item_type == 'Map']


    @property
    def layouts(self):
        """
        Returns all project items which ar of item type "Layout"
        """
        return [it for it in self.items if it.item_type == 'Layout']


    def close(self):
        """
        Closes the ArcGIS Pro project file.
        """
        # All we need to do is to remove the temporary directory with the unzipped content.
        shutil.rmtree(self.tmp_dir)
