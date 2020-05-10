from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import youtubetools
from youtubetools import job_id_hooks
from time import time, sleep
import threading


def get_job_id():
    return str(int(time()*10))


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def template_test():

    lnk = request.form.get('ylink', 'nothing')

    if request.method == 'POST':
        return redirect(url_for("download_page", url=lnk))

    return render_template('index.html')


@app.route("/download", methods=['GET', 'POST'])
def download_page():
    if request.method == 'POST' and request.form.get('res'):
        print(request.form.get("job_id"), " The ID")
        return redirect(url_for("downloading_page", res_code=request.form.get('res'), job_id=request.form.get("job_id")))

    job_id = get_job_id()
    url = request.args.get("url")
    vidobj = youtubetools.To_download(url, job_id)

    return render_template('download.html', my_list=vidobj.id, resolutions=vidobj.formats_l, job_id=job_id)


@app.route("/downloading", methods=['GET', 'POST'])
def downloading_page():
    job_id = request.args.get("job_id")
    format_to_download = request.args.get('res_code')
    dl_obj = job_id_hooks[job_id]
    try:
        dl_obj.d_t(format_to_download)
    except FileExistsError:
        return redirect(url_for("file_already_downloaded"))
    return render_template("downloading.html", job_id=job_id)


@app.route("/downloading/<job_id>", methods=['GET', 'POST'])
def downloading_progress(job_id):
    def stream():
        dct = 0
        while dct < 100:
            sleep(0.5)
            dct = job_id_hooks[job_id].status
            print(dct)
            yield "data:" + str(dct) + "\n\n"
    
    return Response(stream(), mimetype="text/event-stream")


@app.route("/success/")
def success_page():

    return render_template("success.html")


@app.route("/filealreadydownloaded")
def file_already_downloaded():
    return render_template("alreadydownloaded.html")



if __name__ == '__main__':
    app.run(debug=True)
