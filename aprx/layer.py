
import json
import os

from .color import RGBA

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


    @property
    def labels(self):
        """
        Returns a dictionary with some properties for the labels of this layer:
        { shown: true|false, expression: { value, engine }, font: { family, style, size } }
        """
        props = { 'shown': False, 'font': None }
        props['shown'] = self.json.get('labelVisibility', False)
        if props['shown'] is False:
            return props

        label_classes = self.json.get('labelClasses', None)
        if label_classes is None or len(label_classes) == 0:
            return props

        lbl_cls = label_classes[0]
        lbl_symb = lbl_cls['textSymbol']['symbol']

        props['font'] = {
            'family': lbl_symb['fontFamilyName'],
            'style': lbl_symb['fontStyleName'],
            'size': lbl_symb['height']
        }

        props['expression'] = {
            'value': lbl_cls['expression'],
            'engine': lbl_cls['expressionEngine']
        }

        return props


    @property
    def symbol(self):
        """
        Returns a simplified version of the symbol as a dictionary with some of the properties.
        If no symbol is found, None is returned.
        """
        renderer = self.json.get('renderer', None)
        if renderer is None:
            return None

        symb_ref = renderer.get('symbol', None)
        if symb_ref is None:
            return None

        symb_ref_symb = symb_ref.get('symbol', None)
        if symb_ref_symb is None:
            return None

        # Technically, there can be several overlapping symbols. We only extract the *last* one
        # (the one which is rendered on top)
        symb_lyrs = symb_ref_symb.get('symbolLayers', None)
        if symb_lyrs is None or len(symb_lyrs) == 0:
            return None

        symb = symb_lyrs[-1]

        # Extract the fill color which depends on the symbol type
        fcol = None

        if symb['type'] == 'CIMVectorMarker':
            fill = symb['markerGraphics'][-1]['symbol']['symbolLayers'][-1]
            r,g,b,a = fill['color']['values']
            fcol = RGBA(r,g,b,a)

        if symb['type'] == 'CIMCharacterMarker':
            fill = symb['symbol']['symbolLayers'][-1]
            r,g,b,a = fill['color']['values']
            fcol = RGBA(r,g,b,a)

        return {
            'type': symb['type'],
            'enable': symb.get('enable', False),
            'size': symb.get('size', 0),
            'color': fcol
        }


    @property
    def style(self):
        """
        Returns the style for a simple stroke/fill setting.
        """
        renderer = self.json.get('renderer', None)
        if renderer is None:
            return None

        symb_ref = renderer.get('symbol', None)
        if symb_ref is None:
            return None

        symb_ref_symb = symb_ref.get('symbol', None)
        if symb_ref_symb is None:
            return None

        # Initialize an empty style
        stl = { 'fill': None, 'stroke': None }

        # Get the symbol layers and iterate over them to find fill and stroke styles
        symb_lyrs = symb_ref_symb.get('symbolLayers', [])
        for slyr in symb_lyrs:
            if slyr['type'] == 'CIMSolidStroke' and slyr['enable']:
                r,g,b,a = slyr['color']['values']
                stl['stroke'] = {
                    'width': slyr['width'],
                    'color': RGBA(r,g,b,a)
                }

            if slyr['type'] == 'CIMSolidFill' and slyr['enable']:
                r,g,b,a = slyr['color']['values']
                stl['fill'] = {
                    'color': RGBA(r,g,b,a)
                }

        return stl
