# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, abort, send_file, send_from_directory,after_this_request
from flask_cors import CORS, cross_origin
from waitress import serve
import os
import logging

from oiAnalyze import analyze_stock


  
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
logging.basicConfig(filename='server.log',
level=logging.DEBUG,
format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.

@app.route('/download/<path:index>', methods=['POST'])
def download(index):
    analyze_stock(index,request.json)
    file_path = os.path.join(app.root_path, 'data', f'{index}.xlsx')
    app.logger.info(f'{index} file is saved in {file_path}')
    @after_this_request
    def remove_file(res):
        if os.path.isfile(file_path):
            app.logger.info(f'deleting file {file_path}')
            os.remove(file_path)
        return res
    print(os.path.dirname(file_path),file_path)
    return send_from_directory(os.path.dirname(file_path),file_path, f'{index}.xlsx')


  
# main driver function
if __name__ == '__main__':
  
    # run() method of Flask class runs the application 
    # on the local development server.
    # app.run(port=1235)
    port = 5000
    serve(app, host='0.0.0.0', port=port)