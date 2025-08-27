#!/usr/bin/env python3

# Execute with
# $ python3 -m yt_dlp

import sys

if __package__ is None and not getattr(sys, 'frozen', False):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import yt_dlp

if __name__ == '__main__':
    from pprint import pprint

    _TEST_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    argv = [
        "--verbose",
        "-s",
        "-g",
        #"-F",
        _TEST_URL,
        "--list-formats",
        # "-f",
        # "18"
    ]
    
    yt_dlp.main(argv)

    """

    YoutubeDL = yt_dlp.YoutubeDL
    params = {
        'listsubtitles': True,
    }
    with YoutubeDL(params) as ydl:
        resultDict = ydl.extract_info(_TEST_URL, download=False)

    # pprint(resultDict['formats'])
    # pprint([d['format_id'] for d in resultDict['formats']])


    formats = resultDict.get('formats')
    format_ids = map(lambda f: f.get('format_id'), formats)
    # pprint(format_ids)

    tags = ['18']
    ffs = filter(lambda f: f.get('format_id') in tags, formats)
    # height_list = [480]
    # ffs = filter(lambda f: f.get('height') in height_list, formats)
    # pprint(ffs)

    """
