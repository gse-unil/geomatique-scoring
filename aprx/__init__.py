"""
aprx is a small Python modules to extract some basic information from ArcGIS Pro project files
(the .aprx files).
"""

__version__ = '0.1.0'

from .project import Project
from .project_item import ProjectItem
from .layer import Layer
