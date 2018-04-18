from flask import Flask
from flask_restful import Resource, Api, reqparse
from generator import generateMeta

app = Flask(__name__)
api = Api(app)

class RequestAPI(Resource):
    # get requests and parsing
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int)
        parser.add_argument('region', type=int)
        parser.add_argument('party', type=int)
        parser.add_argument('candidate', type=int)
        args = parser.parse_args()
        print(args)

        meta = generateMeta(args)
        return meta

api.add_resource(RequestAPI, '/api', endpoint='api')

if __name__ == '__main__':
    app.run(debug=True)
