import os
from youtube_dl import YoutubeDL
import urllib.parse as urlparse


class To_download():

    def __init__(self, url):
        self.url = url
        self.dlobj = YoutubeDL()
        parsed = urlparse.urlparse(url)
        self.id = urlparse.parse_qs(parsed.query)['v']
        self.id = urlparse.parse_qs(parsed.query)['v']
        self.formats = None

    @property
    def get_formats(self):
        if not self.formats:
            info_dict = self.dlobj.extract_info(self.url, download=False)
            formats = info_dict.get('formats', [info_dict])
            format_codes = [k['format'].split(" - ")[0] for k in formats]
            print(format_codes)
            resolution = [k['format'].split("(")[-1][:-1] for k in formats]
            resolution = [k if k != "tiny" else "audio" for k in resolution]
            ext = [k['ext'] for k in formats]
            filesizes = [str(round(k['filesize']/1000000, 2)) for k in formats]
            self.formats = list(zip(format_codes, resolution, ext, filesizes))

        return self.formats

    @property
    def best_audio(self):
        audio_picker = self.formats
        audio_picker.sort(key=lambda x: float(
            x[-1]) if x[1] == "audio" else -1)
        return audio_picker[-1][0]

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.status = 100.0
        elif d['status'] == 'downloading':
            self.status = float(d["_percent_str"].replace('%', '').strip())

    def download(self, quality, audio_only=False):
        if audio_only:
            self.dlobj = YoutubeDL(
                {'format': f'{self.best_audio}', 'progress_hooks': [self.my_hook]})
            self.dlobj.download([self.url])
            return

        self.dlobj = YoutubeDL(
            {'format': f'{quality}+{self.best_audio}', 'progress_hooks': [self.my_hook]})
        self.dlobj.download([self.url])

def main():
    tst1 = To_download("https://www.youtube.com/watch?v=qFEH0rOBhY4")
    tst1.get_formats
    tst1.download("134")



if __name__ == "__main__":
    main()
