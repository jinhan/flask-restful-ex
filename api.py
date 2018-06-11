from flask import Flask
from flask_restful import Resource, Api, reqparse
from generator import generateMeta
# import argparse
# from orm import run
app = Flask(__name__)
api = Api(app)


# print(config['save'])

class RequestAPI(Resource):
    # get requests and parsing
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int, default=[], action='append')
        parser.add_argument('region', type=int, default=[], action='append')
        parser.add_argument('party', type=int, default=[], action='append')
        parser.add_argument('candidate', type=int, default=[], action='append')
        parser.add_argument('time')
        args = parser.parse_args()
        print(args)

        return generateMeta(args)

api.add_resource(RequestAPI, '/api', endpoint='api')

if __name__ == '__main__':
    # config = argparse.ArgumentParser()
    # config.add_argument('--save', default=True)
    # config = config.parse_args() 
    # app.config['save'] = config['save']
    app.run(host='0.0.0.0', debug=True)


# TODO: production mode