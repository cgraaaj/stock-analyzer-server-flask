# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, abort, send_file, send_from_directory
from flask_cors import CORS, cross_origin
import os

from oiAnalyze import analyze_stock

  
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.

file_to_delete=''

@app.route('/download/<path:index>', methods=['POST'])
def download(index):
    global file_to_delete
    analyze_stock(index,request.json)
    file_path = os.path.join(app.root_path, 'data', f'{index}.xlsx')
    file_to_delete =file_path
    return send_from_directory(os.path.dirname(file_path),file_path,f'{index}.xlsx')

@app.after_request
def remove_file(res):
    if os.path.isfile(file_to_delete):
        os.remove(file_to_delete)
    return res
  
# main driver function
if __name__ == '__main__':
  
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(port=1235)