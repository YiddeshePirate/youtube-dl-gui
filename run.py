import sys
import os
from time import sleep, time

from flask import (Flask, Response, redirect, render_template,
                   request, url_for)

import youtubetools
from youtubetools import job_id_hooks

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder,
                static_folder=static_folder)
else:
    app = Flask(__name__)


def get_job_id():
    return str(int(time() * 10))


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
        return redirect(
            url_for(
                "downloading_page",
                res_code=request.form.get('res'),
                job_id=request.form.get("job_id")))

    job_id = get_job_id()
    url = request.args.get("url")
    try:
        vidobj = youtubetools.To_download(url, job_id)
    except KeyError:
        return render_template("error.html", error="Link looks fishy to me!!")

    except youtubetools.not_found_error:
        return render_template("error.html", error="Video  is  Unavailable!!!")

    print("hello")
    return render_template(
        'download.html',
        my_list=vidobj.id,
        resolutions=vidobj.formats_l,
        job_id=job_id)


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
            yield "data:" + str(dct) + "\n\n"

    return Response(stream(), mimetype="text/event-stream")


@app.route("/done/<job_id>", methods=['GET', 'POST'])
def downloading_done(job_id):
    def stream():
        not_done = True
        while not_done:
            sleep(0.5)
            lst = [job_id_hooks[job_id].id[0],
                   job_id_hooks[job_id].quality, "+"]
            for i in os.listdir():
                if all([k in i for k in lst]) or (
                        job_id_hooks[job_id].quality == "audio" and job_id_hooks[job_id].status >= 100):
                    print("done downloading")
                    yield "data:1\n\n"
                    not_done = False
                else:
                    yield "data:0\n\n"

    return Response(stream(), mimetype="text/event-stream")


@app.route("/success/")
def success_page():
    return render_template("success.html")


@app.route("/filealreadydownloaded")
def file_already_downloaded():
    return render_template("alreadydownloaded.html")


if __name__ == '__main__':
    app.run()
