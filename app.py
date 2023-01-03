from flask import Flask, render_template, request, redirect, send_file
from aws_functions import *
import os

app = Flask(__name__)
BUCKET = "portal-af"
UPLOAD_FOLDER = 'build'

# @app.route("/")
# def hello():
#     return "All this are set.Ready to Go!!!"

@app.route("/")
def home():
    # contents = list_slum_admins()
    return render_template('dashboard.html', contents=list_slum_admins())


@app.route("/upload", methods=['POST'])
def upload_files():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload(f"upload_files/{f.filename}", BUCKET, f.filename)
        return redirect("/home")


@app.route("/download/<filename>", methods=['GET'])
def download_files(filename):
    if request.method == 'GET':
        output = download(filename, BUCKET)
        return send_file(output, as_attachment=True)

#this part isn't used if using frozen
if __name__ == '__main__':
    app.run(debug=True)