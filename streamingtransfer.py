#! /usr/bin/env python
import urllib.request as ur
import urllib.error as ure
import shutil as sh
import time
import os
import sys

def read_meta(response, metalen):
    'Reads the metadata assuming stream byte iter is at the correct location'
    content = response.read(metalen)
    title = content.decode("utf-8", "replace").split(";")
    return title


def read_stream(url, start=False):
    'Reads a single song off of an ice stream'
    outfile = open('streampart.mp3', 'wb')
    request = ur.Request(url)
    request.add_header("Icy-MetaData", 1)
    try:
        response = ur.urlopen(request)
    except ure.URLError as err:
        print(err.reason)
        sys.exit()
    icy_metaint_header = response.headers.get('icy-metaint')
    if icy_metaint_header is None:
        return 'error'
    metaint = int(icy_metaint_header)
    read_length = (metaint + 1)
    content = response.read(read_length)
    metalen = int(content[-1]) * 16
    title = read_meta(response, metalen)[0][13:-1]
    print(title)
    while True:
        content = response.read(read_length)
        outfile.write(content)
        icy_metaint_header = response.headers.get('icy-metaint')
        if icy_metaint_header is not None:
            metalen = int(response.read(1)[-1]) * 16
            if metalen > 0:
                outfile.close()
                if not start:
                    filename = title + '.mp3.unfinished'
                else:
                    filename = title + '.mp3'
                os.rename('streampart.mp3', filename)
                return filename


def usage():
    'see usage.txt'
    usage_text = open('usage.txt', 'r')
    for line in usage_text:
        print(line)


def main(argv):
    'main'
    path = './'
    url = ''
    try:
        url = argv[1]
        path = argv[2]
        if not os.path.exists(path):
            os.makedirs(path)
    except:
        usage()
        exit()
    if url is not None:
        filename = read_stream(url)
        while True:
            time.sleep(15)
            sh.move(filename, path)
            filename = read_stream(url, True)

if __name__ == "__main__":
    main(sys.argv)
