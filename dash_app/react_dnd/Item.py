# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Item(Component):
    """An Item component.
Each task is an item

Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks.
- item (dict; optional): The data of this item"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, item=Component.UNDEFINED, deleteItem=Component.UNDEFINED, moveItem=Component.UNDEFINED, setDragElement=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'item']
        self._type = 'Item'
        self._namespace = 'react_dnd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'item']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Item, self).__init__(**args)
