from flask import Flask, render_template,request, redirect, url_for
import youtubetools
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
        return redirect(url_for("downloading_page", res_code=request.form.get('res'), url = request.args.get("url")))
        print(request.form.get('res'))

    url = request.args.get("url")
    vidobj = youtubetools.To_download(url)
    formats = vidobj.video_formats
    formats = [k for k in formats if k[1] != "audio"]
    formats.sort(key= lambda x:int(x[1][:-1]) if x[1] != "audio" else 0)
    print(f'{url} to download')
    
    return render_template('download.html', my_list=vidobj.id, resolutions=formats)


@app.route("/downloading", methods=['GET', 'POST'])
def downloading_page():
    url = request.args.get("url")
    format_to_download = request.args.get('res_code')
    return render_template("downloading.html")

if __name__ == '__main__':
    app.run(debug=True)