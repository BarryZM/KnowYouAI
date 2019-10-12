import requests

def stream_download(url, savefile, timeout=10):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    response = requests.get(url, headers=headers, stream=True, timeout=timeout)
    with open(savefile, 'wb') as fd:
        for chunk in response.iter_content(128):
            fd.write(chunk)

