from flask import Flask, render_template, request, redirect, send_file, Response
from aws_functions import *
from admin_state_status import *
import os
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


app = Flask(__name__)
BUCKET = "portal-af"
UPLOAD_FOLDER = 'build'


@app.route("/")
def home():
    # contents = list_slum_admins()
    return render_template('dashboard.html', contents=list_slum_admins())

@app.route("/plot_running.png")
def plot_running():
    fig1 = bar_graph_running('admins_running.csv')
    output1 = io.BytesIO()
    FigureCanvas(fig1).print_png(output1)
    return Response(output1.getvalue(), mimetype='image/png')

@app.route("/plot_stopped.png")
def plot_stopped():
    fig2 = bar_graph_stopped('admins_stopped.csv')
    output2 = io.BytesIO(2)
    FigureCanvas(fig2).print_png(output2)
    return Response(output2.getvalue(), mimetype='image/png')

# @app.route('/bar-graphs')
# def bar_graphs():
#     # Generate plots using plt
#     fig1, ax1 = plt.subplots()
#     ax1.bar([1, 2, 3], [3, 2, 1])
#     fig2, ax2 = plt.subplots()
#     ax2.bar([1, 2, 3], [1, 2, 3])

#     # Save plots to memory
#     output1 = io.BytesIO()
#     FigureCanvas(fig1).print_png(output1)
#     output2 = io.BytesIO()
#     FigureCanvas(fig2).print_png(output2)

#     # Return plots as response
#     return Response(output1.getvalue(), mimetype='image/png'), Response(output2.getvalue(), mimetype='image/png')
################################
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    selected_admin = request.args.get('type')
    print(selected_admin) # <-- should print the chosen admin
    return render_template('dashboard.html', title='Admin Details', contents=selected_admin)

###############################
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