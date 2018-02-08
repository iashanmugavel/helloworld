import sys
import json
import boto3
from botocore.exceptions import ClientError
from chalice import Chalice, Response
from chalice import BadRequestError
from chalice import UnauthorizedError
from chalice import NotFoundError
from chalice import CORSConfig
cors_config = CORSConfig(
    allow_origin='https://foo.example.com',
    allow_headers=['X-Special-Header'],
    max_age=600,
    expose_headers=['X-Special-Header'],
    allow_credentials=True
)

S3 = boto3.client('s3', region_name='eu-west-1')
BUCKET = 'shantest21'

app = Chalice(app_name='helloworld')
app.debug = True
CITIES_TO_STATE = {
    'seattle': 'WA',
    'portland': 'OR',
}
OBJECTS = {
}
@app.route('/')
def index():
    return Response(body='hello world!',
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})

@app.route('/cities/{city}')
def state_of_city(city):
    try:
        return {'state': CITIES_TO_STATE[city]}
    except KeyError:
        raise BadRequestError("Unknown city '%s', valid choices are: %s" % (
            city, ', '.join(CITIES_TO_STATE.keys())))

@app.route('/resource/{value}', methods=['PUT'])
def put_test(value):
    return {"value": value}

@app.route('/myview', methods=['POST', 'PUT'])
def myview():
    pass

@app.route('/objects/{key}', methods=['GET', 'PUT'])
def s3objects(key):
    request = app.current_request
    if request.method == 'PUT':
        S3.put_object(Bucket=BUCKET, Key=key,
                      Body=json.dumps(request.json_body))
    elif request.method == 'GET':
        try:
            response = S3.get_object(Bucket=BUCKET, Key=key)
            return json.loads(response['Body'].read())
        except ClientError as e:
            raise NotFoundError(key)

# @app.route('/objects/{key}', methods=['GET', 'PUT'])
# def myobject(key):
#     request = app.current_request
#     if request.method == 'PUT':
#         OBJECTS[key] = request.json_body
#     elif request.method == 'GET':
#         try:
#             return {key: OBJECTS[key]}
#         except KeyError:
#             raise NotFoundError(key)

@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()

@app.route('/supports-cors', methods=['PUT'], cors=True)
def supports_cors():
    return {}
@app.route('/custom_cors', methods=['GET'], cors=cors_config)
def supports_custom_cors():
    return {'cors': True}

@app.route('/authenticated', methods=['GET'], api_key_required=True)
def authenticated():
    return {"secure": True}

        
# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
