from flask import Flask
from flask_restful import Resource, Api, reqparse
import generator

app = Flask(__name__)
api = Api(app)

class RequestAPI(Resource):
    # get requests and parsing
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int, default=None)
        parser.add_argument('region', type=int, default=None)
        parser.add_argument('party', type=int, default=None)
        parser.add_argument('candidate', type=int, default=None)
        args = parser.parse_args()
        print(args)

        meta = generator.generateMeta(args)
        return meta

api.add_resource(RequestAPI, '/api', endpoint='api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
