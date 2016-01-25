# -*- coding: utf-8 -*-
"""
RESTFul module.
"""
from datetime import datetime
from flask_restful import fields


type_mapper = {
    str: fields.String,
    datetime: fields.DateTime(dt_format='iso8601'),
    float: fields.Float,
    int: fields.Integer,
    bool: fields.Boolean}
# TODO: FormattedString Url Arbitrary Nested List Raw Fixed Price


def create_marshaller(keys, types):
    '''Create fields based on default Python types to use with marshal'''
    return {k: type_mapper[v] for k, v in zip(keys, types)}


from flask import Blueprint
from anerp.utils import jsonify
from anerp.reqparse import RequestParsers


class Api:

    def __init__(self, model, request_parsers, marshaller):
        self.model = model
        self.request_parsers = RequestParsers(request_parsers)
        self.marshaller = marshaller
        self.app = Blueprint(model.__name__, __name__, static_folder='static')
        self.url_rules()

    def init_api(self, app):
        app.register_blueprint(self.app)

    def add_url_rule(self, rule, view_func):
        name = view_func.__name__
        self.app.add_url_rule(rule, name, view_func, methods=[name.upper()])

    def url_rules(self):
        self.add_url_rule('/', self.get)
        self.add_url_rule('/<int:id>', self.get)
        self.add_url_rule('/<int:id>', self.patch)
        self.add_url_rule('/<int:id>', self.delete)
        self.add_url_rule('/', self.post)

    @property
    def query(self):
        return self.model.query

    def get(self, id=None):
        data = self.query.get_or_404(id) if id else self.query.all()
        return jsonify(data, self.marshaller)

    def patch(self, id):
        obj = self.query.get_or_404(id)
        args = self.request_parsers('patch')
        for key, value in args.items():
            setattr(obj, key, value)
        obj.update()
        return self.get(id)

    def delete(self, id):
        self.query.get_or_404(id).delete()
        return '', 204

    def post(self):
        args = self.request_parsers('post')
        return self.get(self.model.create(**args).id)
