import json


class dict2obj(object):

    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


def HttpJsonResponse(method, response):
    from tastypie.exceptions import ImmediateHttpResponse
    raise ImmediateHttpResponse(
        response=method(content=json.dumps(response), content_type='application/json; charset=UTF-8'))

