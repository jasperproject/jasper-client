# -*- coding: utf-8 -*-
from jasper import plugin
from flask import  Flask, jsonify, request, Response, abort
#import json
import threading
import logging
from functools import wraps


class RestAPI(object):

    def __init__(self, profile, mic, conversation):
        self.profile = profile
        self.mic = mic
        self.conversation = conversation

        try:
            host = self.profile['restapi']['Host']
        except KeyError:
            host = '127.0.0.1'

        try:
            port = self.profile['restapi']['Port']
        except KeyError:
            port = 5000

        try:
            password = self.profile['restapi']['Password']
        except KeyError:
            password = None

        # create thread for http listener
        t = threading.Thread(target=self.startRestAPI, args=(host, port, password))
        t.daemon = True
        t.start()

    def startRestAPI(self, host, port, password):
        app = Flask(__name__)

        def requires_auth(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth = request.authorization
                if password and (not auth or auth.password != password):
                    return Response(
                    'Authorization required.', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})
                return f(*args, **kwargs)
            return decorated
            
        
        @app.route('/')
        def index():
            return "Jasper restAPI: running"

        @app.route('/jasper/say', methods=['POST'])
        @requires_auth
        def say_task():
            if not request.json or not 'text' in request.json:
                abort(400)
            text = request.json['text']

            self.conversation.suspend()
            self.mic.say(text)
            self.conversation.resume()

            return jsonify({'say': text}), 201

        @app.route('/jasper/transcribe', methods=['GET'])
        @requires_auth
        def transcribe_task():
            self.conversation.suspend()
            transcribed = self.mic.active_listen()
            self.conversation.resume()

            return jsonify({'transcribed':transcribed}), 201

        @app.route('/jasper/activate', methods=['GET'])
        @requires_auth
        def activate_task():
            self.conversation.suspend()
            transcribed = self.mic.active_listen()
            result = self.conversation.handleInput(transcribed)
            self.conversation.resume()

            return jsonify({'transcribed':transcribed, 'result':result}), 201

        @app.route('/jasper/handleinput', methods=['POST'])
        @requires_auth
        def handleinput_task():
            if not request.json or not 'text' in request.json:
                abort(400)
            text = request.json['text']

            self.conversation.suspend()
            result = self.conversation.handleInput([text])
            self.conversation.resume()

            return jsonify({'text':text, 'result':result}), 201

        @app.route('/jasper/waitforkeyword', methods=['POST'])
        @requires_auth
        def waitforkeyword_task():
            if not request.json or not 'keyword' in request.json:
                abort(400)
            keyword = request.json['keyword']

            self.conversation.suspend()
            self.mic.wait_for_keyword(keyword)
            self.conversation.resume()

            return jsonify({'keyword': keyword}), 201

        @app.route('/jasper/playfile', methods=['POST'])
        @requires_auth
        def playfile_task():
            if not request.json or not 'filename' in request.json:
                abort(400)
            filename = request.json['filename']

            self.conversation.suspend()
            self.mic.play_file(filename)
            self.conversation.resume()

            return jsonify({'filename': filename}), 201


        # start http listener
        app.run(host=host, port=port, debug=False)