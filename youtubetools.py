import os
from youtube_dl import YoutubeDL
import urllib.parse as urlparse
import threading
import time

job_id_hooks = {}

class To_download():

    def __init__(self, url, job_id):
        global job_id_hooks
        self.job_id = job_id
        self.url = url
        self.dlobj = YoutubeDL({'quiet': True})
        parsed = urlparse.urlparse(url)
        self.id = urlparse.parse_qs(parsed.query)['v']
        self.id = urlparse.parse_qs(parsed.query)['v']
        self.formats = None
        self.status = -1
        job_id_hooks[self.job_id] = self
        

    @property
    def get_formats(self):
        if not self.formats:
            info_dict = self.dlobj.extract_info(self.url, download=False)
            formats = info_dict.get('formats', [info_dict])
            format_codes = [k['format'].split(" - ")[0] for k in formats]
            resolution = [k['format'].split("(")[-1][:-1] for k in formats]
            resolution = [k if k != "tiny" else "audio" for k in resolution]
            ext = [k['ext'] for k in formats]
            filesizes = [k['filesize'] if k['filesize']
                         else 0 for k in formats]
            filesizes = [str(round(k/1000000, 2)) for k in filesizes]
            self.formats = list(zip(format_codes, resolution, ext, filesizes))

        return self.formats

    @property
    def best_audio(self):
        self.get_formats
        audio_picker = self.formats
        audio_picker.sort(key=lambda x: float(
            x[-1]) if x[1] == "audio" else -1)
        return audio_picker[-1][0]

    @property
    def video_formats(self):
        self.get_formats
        return [k for k in self.get_formats if k[1] != "audio"]

    @property
    def formats_l(self):
        formats_l = self.video_formats
        formats_l = [k for k in formats_l if k[1] != "audio"]
        formats_l.sort(key=lambda x: int(x[1][:x[1].find("p")]) if x[1] != "audio" else 0)
        return formats_l

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.status = 100.0
        elif d['status'] == 'downloading':
            new_status = float(d["_percent_str"].replace('%', '').strip())
            self.status = max(new_status, self.status)

    def download(self, quality, audio_only=False):
        if quality == "audio":
            self.dlobj = YoutubeDL(
                {'format': f'{self.best_audio}', 'progress_hooks': [self.my_hook], 'quiet': True})
            self.dlobj.download([self.url])
            return

        self.dlobj = YoutubeDL(
            {'format': f'{quality}+{self.best_audio}', 'progress_hooks': [self.my_hook], 'quiet': True})
        self.dlobj.download([self.url])
    

    def d_t(self, quality, audio_only=False):
        x = threading.Thread(target=self.download, args=(quality, audio_only))
        x.start()


def main():
    tst1 = To_download("https://www.youtube.com/watch?v=D_EX9FUDv3o")
    x = threading.Thread(target=tst1.download, args=("243",))
    x.start()
    for i in range(10):
        time.sleep(3)
        print(f'\n{tst1.status}\n')
    x.join()


if __name__ == "__main__":
    main()
