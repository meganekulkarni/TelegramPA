# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ReactDnd(Component):
    """A ReactDnd component.
ReactDnd takes an array of data and statuses 
and displays them in columns for the user to drag
and update their status.

Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks.
- statuses (list; required): List of status columns for each task
- data (list; required): A list of current tasks and their status"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, statuses=Component.REQUIRED, data=Component.REQUIRED, **kwargs):
        self._prop_names = ['id', 'statuses', 'data']
        self._type = 'ReactDnd'
        self._namespace = 'react_dnd'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'statuses', 'data']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['statuses', 'data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ReactDnd, self).__init__(**args)
