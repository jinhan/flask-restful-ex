from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class RequestCards(Resource):
    # get requests and parsing
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int)
        parser.add_argument('region', type=int)
        parser.add_argument('party', type=int)
        parser.add_argument('candidate', type=int)
        args = parser.parse_args()
        print(args)

        return args
        # return generateCards(args)

    # create cards and return json
    # def generateCards(self, args):
        # match name from id

class RequestImages(Resource):
    def post(self):
        return {'status': 'success'}

api.add_resource(RequestCards, '/cards', endpoint='cards')
api.add_resource(RequestImages, '/images', endpoint='images')

if __name__ == '__main__':
    app.run(debug=True)
