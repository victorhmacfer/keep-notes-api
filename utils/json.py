
from json import JSONEncoder
from flask import make_response

def make_json_response(resp_dict, status_code):
    resp_body = JSONEncoder(indent=4, separators=(',', ': ')).encode(resp_dict)
    response = make_response(resp_body, status_code)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response
