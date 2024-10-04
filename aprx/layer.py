
import json
import os

class Layer:
    def __init__(self, project, layer_path):
        self.project = project
        self.path = layer_path

        # Read the content from the JSON
        with open(os.path.join(self.project.tmp_dir, self.path), 'r', encoding='utf-8') as f:
            self.json = json.loads(f.read())

    @property
    def id(self):
        """
        Returns an ID for the layer. This is the name of the layer definition file in the APRX file.
        Most of the time, this is just the lowercase string of the layer name, but it avoids
        duplicate names.
        """
        return os.path.splitext(os.path.basename(self.path))[0]


    @property
    def name(self):
        """
        The name of the layer as in the layer tree.
        """
        return self.json.get('name', None)
