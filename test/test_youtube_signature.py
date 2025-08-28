b'--- ./test/test_youtube_signature.py\t(original)'
b'+++ ./test/test_youtube_signature.py\t(refactored)'
b'@@ -1,9 +1,12 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' import unittest'
b'+from io import open'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -11,7 +14,7 @@'
b' import contextlib'
b' import re'
b' import string'
b'-import urllib.request'
b'+import urllib2, urllib'
b' '
b' from test.helper import FakeYDL, is_download_test'
b' from yt_dlp.extractor import YoutubeIE'
b'@@ -19,425 +22,425 @@'
b' '
b' _SIG_TESTS = ['
b'     ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-vflHOr_nV.js',"
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-vflHOr_nV.js',"
b'         86,'
b'-        \'>=<;:/.-[+*)(\\\'&%$#"!ZYX0VUTSRQPONMLKJIHGFEDCBA\\\\yxwvutsrqponmlkjihgfedcba987654321\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-vfldJ8xgI.js',"
b'+        u\'>=<;:/.-[+*)(\\\'&%$#"!ZYX0VUTSRQPONMLKJIHGFEDCBA\\\\yxwvutsrqponmlkjihgfedcba987654321\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-vfldJ8xgI.js',"
b'         85,'
b'-        \'3456789a0cdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRS[UVWXYZ!"#$%&\\\'()*+,-./:;<=>?@\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-vfle-mVwz.js',"
b'+        u\'3456789a0cdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRS[UVWXYZ!"#$%&\\\'()*+,-./:;<=>?@\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-vfle-mVwz.js',"
b'         90,'
b'-        \']\\\\[@?>=<;:/.-,+*)(\\\'&%$#"hZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjiagfedcb39876\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vfl0Cbn9e.js',"
b'+        u\']\\\\[@?>=<;:/.-,+*)(\\\'&%$#"hZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjiagfedcb39876\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vfl0Cbn9e.js',"
b'         84,'
b'-        \'O1I3456789abcde0ghijklmnopqrstuvwxyzABCDEFGHfJKLMN2PQRSTUVW@YZ!"#$%&\\\'()*+,-./:;<=\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflXGBaUN.js',"
b"-        '2ACFC7A61CA478CD21425E5A57EBD73DDC78E22A.2094302436B2D377D14A3BBA23022D023B8BC25AA',"
b"-        'A52CB8B320D22032ABB3A41D773D2B6342034902.A22E87CDD37DBE75A5E52412DC874AC16A7CFCA2',"
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflBb0OQx.js',"
b'+        u\'O1I3456789abcde0ghijklmnopqrstuvwxyzABCDEFGHfJKLMN2PQRSTUVW@YZ!"#$%&\\\'()*+,-./:;<=\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflXGBaUN.js',"
b"+        u'2ACFC7A61CA478CD21425E5A57EBD73DDC78E22A.2094302436B2D377D14A3BBA23022D023B8BC25AA',"
b"+        u'A52CB8B320D22032ABB3A41D773D2B6342034902.A22E87CDD37DBE75A5E52412DC874AC16A7CFCA2',"
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflBb0OQx.js',"
b'         84,'
b'-        \'123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ0STUVWXYZ!"#$%&\\\'()*+,@./:;<=>\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vfl9FYC6l.js',"
b'+        u\'123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ0STUVWXYZ!"#$%&\\\'()*+,@./:;<=>\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vfl9FYC6l.js',"
b'         83,'
b'-        \'123456789abcdefghijklmnopqr0tuvwxyzABCDETGHIJKLMNOPQRS>UVWXYZ!"#$%&\\\'()*+,-./:;<=F\','
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflCGk6yw/html5player.js',"
b"-        '4646B5181C6C3020DF1D9C7FCFEA.AD80ABF70C39BD369CCCAE780AFBB98FA6B6CB42766249D9488C288',"
b"-        '82C8849D94266724DC6B6AF89BBFA087EACCD963.B93C07FBA084ACAEFCF7C9D1FD0203C6C1815B6B',"
b'-    ),'
b'-    ('
b"-        'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflKjOTVq/html5player.js',"
b"-        '312AA52209E3623129A412D56A40F11CB0AF14AE.3EE09501CB14E3BCDC3B2AE808BF3F1D14E7FBF12',"
b"-        '112AA5220913623229A412D56A40F11CB0AF14AE.3EE0950FCB14EEBCDC3B2AE808BF331D14E7FBF3',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/6ed0d907/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'AOq0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL2QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/3bb1f723/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'MyOSJXtKI3m-uME_jv7-pT12gOFC02RFkGoqWpzE0Cs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/2f1832d2/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xxAj7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJ2OySqa0q',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'AAOAOq0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xx8j7vgpDL0QwbdV06sCIEzpWqMGkFR20CFOS21Tp-7vj_EMu-m37KtXJoOy1',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/363db69b/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpz2ICs6EVdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/363db69b/player_ias_tce.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpz2ICs6EVdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/4fcd6e4a/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'wAOAOq0QJ8ARAIgXmPlOPSBkkUs1bYFYlJCfe29xx8q7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/4fcd6e4a/player_ias_tce.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'wAOAOq0QJ8ARAIgXmPlOPSBkkUs1bYFYlJCfe29xx8q7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player_ias.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player_ias_tce.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player-plasma-ias-phone-en_US.vflset/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player-plasma-ias-tablet-en_US.vflset/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        '7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8a8ac953/player_ias_tce.vflset/en_US/base.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'IAOAOq0QJ8wRAAgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_E2u-m37KtXJoOySqa0',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8a8ac953/tv-player-es6.vflset/tv-player-es6.js',"
b"-        '2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"-        'IAOAOq0QJ8wRAAgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_E2u-m37KtXJoOySqa0',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/e12fbea4/player_ias.vflset/en_US/base.js',"
b"-        'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"-        'JC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit0zJAtIEsgOV2SXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-a',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/010fbc8d/player_es5.vflset/en_US/base.js',"
b"-        'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"-        'ttJC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit2zJAsIEggOVaSXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/010fbc8d/player_es6.vflset/en_US/base.js',"
b"-        'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"-        'ttJC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit2zJAsIEggOVaSXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/5ec65609/player_ias_tcc.vflset/en_US/base.js',"
b"-        'AAJAJfQdSswRAIgNSN0GDUcHnCIXkKcF61yLBgDHiX1sUhOJdY4_GxunRYCIDeYNYP_16mQTPm5f1OVq3oV1ijUNYPjP4iUSMAjO9bZ',"
b"-        'AJfQdSswRAIgNSN0GDUcHnCIXkKcF61ZLBgDHiX1sUhOJdY4_GxunRYCIDyYNYP_16mQTPm5f1OVq3oV1ijUNYPjP4iUSMAjO9be',"
b'+        u\'123456789abcdefghijklmnopqr0tuvwxyzABCDETGHIJKLMNOPQRS>UVWXYZ!"#$%&\\\'()*+,-./:;<=F\','
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflCGk6yw/html5player.js',"
b"+        u'4646B5181C6C3020DF1D9C7FCFEA.AD80ABF70C39BD369CCCAE780AFBB98FA6B6CB42766249D9488C288',"
b"+        u'82C8849D94266724DC6B6AF89BBFA087EACCD963.B93C07FBA084ACAEFCF7C9D1FD0203C6C1815B6B',"
b'+    ),'
b'+    ('
b"+        u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflKjOTVq/html5player.js',"
b"+        u'312AA52209E3623129A412D56A40F11CB0AF14AE.3EE09501CB14E3BCDC3B2AE808BF3F1D14E7FBF12',"
b"+        u'112AA5220913623229A412D56A40F11CB0AF14AE.3EE0950FCB14EEBCDC3B2AE808BF331D14E7FBF3',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/6ed0d907/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'AOq0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL2QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/3bb1f723/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'MyOSJXtKI3m-uME_jv7-pT12gOFC02RFkGoqWpzE0Cs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/2f1832d2/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xxAj7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJ2OySqa0q',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'AAOAOq0QJ8wRAIgXmPlOPSBkkUs1bYFYlJCfe29xx8j7vgpDL0QwbdV06sCIEzpWqMGkFR20CFOS21Tp-7vj_EMu-m37KtXJoOy1',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/363db69b/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpz2ICs6EVdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/363db69b/player_ias_tce.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpz2ICs6EVdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/4fcd6e4a/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'wAOAOq0QJ8ARAIgXmPlOPSBkkUs1bYFYlJCfe29xx8q7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/4fcd6e4a/player_ias_tce.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'wAOAOq0QJ8ARAIgXmPlOPSBkkUs1bYFYlJCfe29xx8q7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player_ias.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player_ias_tce.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player-plasma-ias-phone-en_US.vflset/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player-plasma-ias-tablet-en_US.vflset/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'7AOq0QJ8wRAIgXmPlOPSBkkAs1bYFYlJCfe29xx8jOv1pDL0Q2bdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_EMu-m37KtXJoOySqa0qaw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8a8ac953/player_ias_tce.vflset/en_US/base.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'IAOAOq0QJ8wRAAgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_E2u-m37KtXJoOySqa0',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8a8ac953/tv-player-es6.vflset/tv-player-es6.js',"
b"+        u'2aq0aqSyOoJXtK73m-uME_jv7-pT15gOFC02RFkGMqWpzEICs69VdbwQ0LDp1v7j8xx92efCJlYFYb1sUkkBSPOlPmXgIARw8JQ0qOAOAA',"
b"+        u'IAOAOq0QJ8wRAAgXmPlOPSBkkUs1bYFYlJCfe29xx8j7v1pDL0QwbdV96sCIEzpWqMGkFR20CFOg51Tp-7vj_E2u-m37KtXJoOySqa0',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/e12fbea4/player_ias.vflset/en_US/base.js',"
b"+        u'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"+        u'JC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit0zJAtIEsgOV2SXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-a',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/010fbc8d/player_es5.vflset/en_US/base.js',"
b"+        u'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"+        u'ttJC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit2zJAsIEggOVaSXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/010fbc8d/player_es6.vflset/en_US/base.js',"
b"+        u'gN7a-hudCuAuPH6fByOk1_GNXN0yNMHShjZXS2VOgsEItAJz0tipeavEOmNdYN-wUtcEqD3bCXjc0iyKfAyZxCBGgIARwsSdQfJ2CJtt',"
b"+        u'ttJC2JfQdSswRAIgGBCxZyAfKyi0cjXCb3DqEctUw-NYdNmOEvaepit2zJAsIEggOVaSXZjhSHMNy0NXNG_1kOyBf6HPuAuCduh-',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/5ec65609/player_ias_tcc.vflset/en_US/base.js',"
b"+        u'AAJAJfQdSswRAIgNSN0GDUcHnCIXkKcF61yLBgDHiX1sUhOJdY4_GxunRYCIDeYNYP_16mQTPm5f1OVq3oV1ijUNYPjP4iUSMAjO9bZ',"
b"+        u'AJfQdSswRAIgNSN0GDUcHnCIXkKcF61ZLBgDHiX1sUhOJdY4_GxunRYCIDyYNYP_16mQTPm5f1OVq3oV1ijUNYPjP4iUSMAjO9be',"
b'     ),'
b' ]'
b' '
b' _NSIG_TESTS = ['
b'     ('
b"-        'https://www.youtube.com/s/player/7862ca1f/player_ias.vflset/en_US/base.js',"
b"-        'X_LCxVDjAavgE5t', 'yxJ1dM6iz5ogUg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/9216d1f7/player_ias.vflset/en_US/base.js',"
b"-        'SLp9F5bwjAdhE9F-', 'gWnb9IK2DJ8Q1w',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/f8cb7a3b/player_ias.vflset/en_US/base.js',"
b"-        'oBo2h5euWy6osrUt', 'ivXHpm7qJjJN',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/2dfe380c/player_ias.vflset/en_US/base.js',"
b"-        'oBo2h5euWy6osrUt', '3DIBbn3qdQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/f1ca6900/player_ias.vflset/en_US/base.js',"
b"-        'cu3wyu6LQn2hse', 'jvxetvmlI9AN9Q',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8040e515/player_ias.vflset/en_US/base.js',"
b"-        'wvOFaY-yjgDuIEg5', 'HkfBFDHmgw4rsw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/e06dea74/player_ias.vflset/en_US/base.js',"
b"-        'AiuodmaDDYw8d3y4bf', 'ankd8eza2T6Qmw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/5dd88d1d/player-plasma-ias-phone-en_US.vflset/base.js',"
b"-        'kSxKFLeqzv_ZyHSAt', 'n8gS8oRlHOxPFA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/324f67b9/player_ias.vflset/en_US/base.js',"
b"-        'xdftNy7dh9QGnhW', '22qLGxrmX8F1rA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/4c3f79c5/player_ias.vflset/en_US/base.js',"
b"-        'TDCstCG66tEAO5pR9o', 'dbxNtZ14c-yWyw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/c81bbb4a/player_ias.vflset/en_US/base.js',"
b"-        'gre3EcLurNY2vqp94', 'Z9DfGxWP115WTg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/1f7d5369/player_ias.vflset/en_US/base.js',"
b"-        'batNX7sYqIJdkJ', 'IhOkL_zxbkOZBw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/009f1d77/player_ias.vflset/en_US/base.js',"
b"-        '5dwFHw8aFWQUQtffRq', 'audescmLUzI3jw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/dc0c6770/player_ias.vflset/en_US/base.js',"
b"-        '5EHDMgYLV6HPGk_Mu-kk', 'n9lUJLHbxUI0GQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/113ca41c/player_ias.vflset/en_US/base.js',"
b"-        'cgYl-tlYkhjT7A', 'hI7BBr2zUgcmMg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/c57c113c/player_ias.vflset/en_US/base.js',"
b"-        'M92UUMHa8PdvPd3wyM', '3hPqLJsiNZx7yA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/5a3b6271/player_ias.vflset/en_US/base.js',"
b"-        'B2j7f_UPT4rfje85Lu_e', 'm5DmNymaGQ5RdQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/7a062b77/player_ias.vflset/en_US/base.js',"
b"-        'NRcE3y3mVtm_cV-W', 'VbsCYUATvqlt5w',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/dac945fd/player_ias.vflset/en_US/base.js',"
b"-        'o8BkRxXhuYsBCWi6RplPdP', '3Lx32v_hmzTm6A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/6f20102c/player_ias.vflset/en_US/base.js',"
b"-        'lE8DhoDmKqnmJJ', 'pJTTX6XyJP2BYw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/cfa9e7cb/player_ias.vflset/en_US/base.js',"
b"-        'aCi3iElgd2kq0bxVbQ', 'QX1y8jGb2IbZ0w',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8c7583ff/player_ias.vflset/en_US/base.js',"
b"-        '1wWCVpRR96eAmMI87L', 'KSkWAVv1ZQxC3A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/b7910ca8/player_ias.vflset/en_US/base.js',"
b"-        '_hXMCwMt9qE310D', 'LoZMgkkofRMCZQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/590f65a6/player_ias.vflset/en_US/base.js',"
b"-        '1tm7-g_A9zsI8_Lay_', 'xI4Vem4Put_rOg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/b22ef6e7/player_ias.vflset/en_US/base.js',"
b"-        'b6HcntHGkvBLk_FRf', 'kNPW6A7FyP2l8A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/3400486c/player_ias.vflset/en_US/base.js',"
b"-        'lL46g3XifCKUZn1Xfw', 'z767lhet6V2Skl',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20dfca59/player_ias.vflset/en_US/base.js',"
b"-        '-fLCxedkAk4LUTK2', 'O8kfRq1y1eyHGw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/b12cc44b/player_ias.vflset/en_US/base.js',"
b"-        'keLa5R2U00sR9SQK', 'N1OGyujjEwMnLw',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/3bb1f723/player_ias.vflset/en_US/base.js',"
b"-        'gK15nzVyaXE9RsMP3z', 'ZFFWFLPWx9DEgQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/2f1832d2/player_ias.vflset/en_US/base.js',"
b"-        'YWt1qdbe8SAfkoPHW5d', 'RrRjWQOJmBiP',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/9c6dfc4a/player_ias.vflset/en_US/base.js',"
b"-        'jbu7ylIosQHyJyJV', 'uwI0ESiynAmhNg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/e7567ecf/player_ias_tce.vflset/en_US/base.js',"
b"-        'Sy4aDGc0VpYRR9ew_', '5UPOT1VhoZxNLQ',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/d50f54ef/player_ias_tce.vflset/en_US/base.js',"
b"-        'Ha7507LzRmH3Utygtj', 'XFTb2HoeOE5MHg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/074a8365/player_ias_tce.vflset/en_US/base.js',"
b"-        'Ha7507LzRmH3Utygtj', 'ufTsrE0IVYrkl8v',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/643afba4/player_ias.vflset/en_US/base.js',"
b"-        'N5uAlLqm0eg1GyHO', 'dCBQOejdq5s-ww',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/69f581a5/tv-player-ias.vflset/tv-player-ias.js',"
b"-        '-qIP447rVlTTwaZjY', 'KNcGOksBAvwqQg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js',"
b"-        'ir9-V6cdbCiyKxhr', '2PL7ZDYAALMfmA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/363db69b/player_ias.vflset/en_US/base.js',"
b"-        'eWYu5d5YeY_4LyEDc', 'XJQqf-N7Xra3gg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/4fcd6e4a/player_ias.vflset/en_US/base.js',"
b"-        'o_L251jm8yhZkWtBW', 'lXoxI3XvToqn6A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/4fcd6e4a/player_ias_tce.vflset/en_US/base.js',"
b"-        'o_L251jm8yhZkWtBW', 'lXoxI3XvToqn6A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/tv-player-ias.vflset/tv-player-ias.js',"
b"-        'ir9-V6cdbCiyKxhr', '9YE85kNjZiS4',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player-plasma-ias-phone-en_US.vflset/base.js',"
b"-        'ir9-V6cdbCiyKxhr', '9YE85kNjZiS4',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20830619/player-plasma-ias-tablet-en_US.vflset/base.js',"
b"-        'ir9-V6cdbCiyKxhr', '9YE85kNjZiS4',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8a8ac953/player_ias_tce.vflset/en_US/base.js',"
b"-        'MiBYeXx_vRREbiCCmh', 'RtZYMVvmkE0JE',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8a8ac953/tv-player-es6.vflset/tv-player-es6.js',"
b"-        'MiBYeXx_vRREbiCCmh', 'RtZYMVvmkE0JE',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/59b252b9/player_ias.vflset/en_US/base.js',"
b"-        'D3XWVpYgwhLLKNK4AGX', 'aZrQ1qWJ5yv5h',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/fc2a56a5/player_ias.vflset/en_US/base.js',"
b"-        'qTKWg_Il804jd2kAC', 'OtUAm2W6gyzJjB9u',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/fc2a56a5/tv-player-ias.vflset/tv-player-ias.js',"
b"-        'qTKWg_Il804jd2kAC', 'OtUAm2W6gyzJjB9u',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/a74bf670/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', 'hQP7k1hA22OrNTnq',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/6275f73c/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '-I03XF0iyf6I_X0A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/20c72c18/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '-I03XF0iyf6I_X0A',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/9fe2e06e/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '6r5ekNIiEMPutZy',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/680f8c75/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '0ml9caTwpa55Jf',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/14397202/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', 'ozZFAN21okDdJTa',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/5dcb2c1f/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', 'p7iTbRZDYAF',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/a10d7fcc/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '9Zue7DDHJSD',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/8e20cb06/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', '5-4tTneTROTpMzba',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/e12fbea4/player_ias_tce.vflset/en_US/base.js',"
b"-        'kM5r52fugSZRAKHfo3', 'XkeRfXIPOkSwfg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/ef259203/player_ias_tce.vflset/en_US/base.js',"
b"-        'rPqBC01nJpqhhi2iA2U', 'hY7dbiKFT51UIA',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/010fbc8d/player_es5.vflset/en_US/base.js',"
b"-        '0hlOAlqjFszVvF4Z', 'R-H23bZGAsRFTg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/010fbc8d/player_es6.vflset/en_US/base.js',"
b"-        '0hlOAlqjFszVvF4Z', 'R-H23bZGAsRFTg',"
b'-    ),'
b'-    ('
b"-        'https://www.youtube.com/s/player/5ec65609/player_ias_tcc.vflset/en_US/base.js',"
b"-        '6l5CTNx4AzIqH4MXM', 'NupToduxHBew1g',"
b"+        u'https://www.youtube.com/s/player/7862ca1f/player_ias.vflset/en_US/base.js',"
b"+        u'X_LCxVDjAavgE5t', u'yxJ1dM6iz5ogUg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/9216d1f7/player_ias.vflset/en_US/base.js',"
b"+        u'SLp9F5bwjAdhE9F-', u'gWnb9IK2DJ8Q1w',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/f8cb7a3b/player_ias.vflset/en_US/base.js',"
b"+        u'oBo2h5euWy6osrUt', u'ivXHpm7qJjJN',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/2dfe380c/player_ias.vflset/en_US/base.js',"
b"+        u'oBo2h5euWy6osrUt', u'3DIBbn3qdQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/f1ca6900/player_ias.vflset/en_US/base.js',"
b"+        u'cu3wyu6LQn2hse', u'jvxetvmlI9AN9Q',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8040e515/player_ias.vflset/en_US/base.js',"
b"+        u'wvOFaY-yjgDuIEg5', u'HkfBFDHmgw4rsw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/e06dea74/player_ias.vflset/en_US/base.js',"
b"+        u'AiuodmaDDYw8d3y4bf', u'ankd8eza2T6Qmw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/5dd88d1d/player-plasma-ias-phone-en_US.vflset/base.js',"
b"+        u'kSxKFLeqzv_ZyHSAt', u'n8gS8oRlHOxPFA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/324f67b9/player_ias.vflset/en_US/base.js',"
b"+        u'xdftNy7dh9QGnhW', u'22qLGxrmX8F1rA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/4c3f79c5/player_ias.vflset/en_US/base.js',"
b"+        u'TDCstCG66tEAO5pR9o', u'dbxNtZ14c-yWyw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/c81bbb4a/player_ias.vflset/en_US/base.js',"
b"+        u'gre3EcLurNY2vqp94', u'Z9DfGxWP115WTg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/1f7d5369/player_ias.vflset/en_US/base.js',"
b"+        u'batNX7sYqIJdkJ', u'IhOkL_zxbkOZBw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/009f1d77/player_ias.vflset/en_US/base.js',"
b"+        u'5dwFHw8aFWQUQtffRq', u'audescmLUzI3jw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/dc0c6770/player_ias.vflset/en_US/base.js',"
b"+        u'5EHDMgYLV6HPGk_Mu-kk', u'n9lUJLHbxUI0GQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/113ca41c/player_ias.vflset/en_US/base.js',"
b"+        u'cgYl-tlYkhjT7A', u'hI7BBr2zUgcmMg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/c57c113c/player_ias.vflset/en_US/base.js',"
b"+        u'M92UUMHa8PdvPd3wyM', u'3hPqLJsiNZx7yA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/5a3b6271/player_ias.vflset/en_US/base.js',"
b"+        u'B2j7f_UPT4rfje85Lu_e', u'm5DmNymaGQ5RdQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/7a062b77/player_ias.vflset/en_US/base.js',"
b"+        u'NRcE3y3mVtm_cV-W', u'VbsCYUATvqlt5w',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/dac945fd/player_ias.vflset/en_US/base.js',"
b"+        u'o8BkRxXhuYsBCWi6RplPdP', u'3Lx32v_hmzTm6A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/6f20102c/player_ias.vflset/en_US/base.js',"
b"+        u'lE8DhoDmKqnmJJ', u'pJTTX6XyJP2BYw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/cfa9e7cb/player_ias.vflset/en_US/base.js',"
b"+        u'aCi3iElgd2kq0bxVbQ', u'QX1y8jGb2IbZ0w',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8c7583ff/player_ias.vflset/en_US/base.js',"
b"+        u'1wWCVpRR96eAmMI87L', u'KSkWAVv1ZQxC3A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/b7910ca8/player_ias.vflset/en_US/base.js',"
b"+        u'_hXMCwMt9qE310D', u'LoZMgkkofRMCZQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/590f65a6/player_ias.vflset/en_US/base.js',"
b"+        u'1tm7-g_A9zsI8_Lay_', u'xI4Vem4Put_rOg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/b22ef6e7/player_ias.vflset/en_US/base.js',"
b"+        u'b6HcntHGkvBLk_FRf', u'kNPW6A7FyP2l8A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/3400486c/player_ias.vflset/en_US/base.js',"
b"+        u'lL46g3XifCKUZn1Xfw', u'z767lhet6V2Skl',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20dfca59/player_ias.vflset/en_US/base.js',"
b"+        u'-fLCxedkAk4LUTK2', u'O8kfRq1y1eyHGw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/b12cc44b/player_ias.vflset/en_US/base.js',"
b"+        u'keLa5R2U00sR9SQK', u'N1OGyujjEwMnLw',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/3bb1f723/player_ias.vflset/en_US/base.js',"
b"+        u'gK15nzVyaXE9RsMP3z', u'ZFFWFLPWx9DEgQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/2f1832d2/player_ias.vflset/en_US/base.js',"
b"+        u'YWt1qdbe8SAfkoPHW5d', u'RrRjWQOJmBiP',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/9c6dfc4a/player_ias.vflset/en_US/base.js',"
b"+        u'jbu7ylIosQHyJyJV', u'uwI0ESiynAmhNg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/e7567ecf/player_ias_tce.vflset/en_US/base.js',"
b"+        u'Sy4aDGc0VpYRR9ew_', u'5UPOT1VhoZxNLQ',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/d50f54ef/player_ias_tce.vflset/en_US/base.js',"
b"+        u'Ha7507LzRmH3Utygtj', u'XFTb2HoeOE5MHg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/074a8365/player_ias_tce.vflset/en_US/base.js',"
b"+        u'Ha7507LzRmH3Utygtj', u'ufTsrE0IVYrkl8v',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/643afba4/player_ias.vflset/en_US/base.js',"
b"+        u'N5uAlLqm0eg1GyHO', u'dCBQOejdq5s-ww',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/69f581a5/tv-player-ias.vflset/tv-player-ias.js',"
b"+        u'-qIP447rVlTTwaZjY', u'KNcGOksBAvwqQg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js',"
b"+        u'ir9-V6cdbCiyKxhr', u'2PL7ZDYAALMfmA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/363db69b/player_ias.vflset/en_US/base.js',"
b"+        u'eWYu5d5YeY_4LyEDc', u'XJQqf-N7Xra3gg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/4fcd6e4a/player_ias.vflset/en_US/base.js',"
b"+        u'o_L251jm8yhZkWtBW', u'lXoxI3XvToqn6A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/4fcd6e4a/player_ias_tce.vflset/en_US/base.js',"
b"+        u'o_L251jm8yhZkWtBW', u'lXoxI3XvToqn6A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/tv-player-ias.vflset/tv-player-ias.js',"
b"+        u'ir9-V6cdbCiyKxhr', u'9YE85kNjZiS4',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player-plasma-ias-phone-en_US.vflset/base.js',"
b"+        u'ir9-V6cdbCiyKxhr', u'9YE85kNjZiS4',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20830619/player-plasma-ias-tablet-en_US.vflset/base.js',"
b"+        u'ir9-V6cdbCiyKxhr', u'9YE85kNjZiS4',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8a8ac953/player_ias_tce.vflset/en_US/base.js',"
b"+        u'MiBYeXx_vRREbiCCmh', u'RtZYMVvmkE0JE',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8a8ac953/tv-player-es6.vflset/tv-player-es6.js',"
b"+        u'MiBYeXx_vRREbiCCmh', u'RtZYMVvmkE0JE',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/59b252b9/player_ias.vflset/en_US/base.js',"
b"+        u'D3XWVpYgwhLLKNK4AGX', u'aZrQ1qWJ5yv5h',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/fc2a56a5/player_ias.vflset/en_US/base.js',"
b"+        u'qTKWg_Il804jd2kAC', u'OtUAm2W6gyzJjB9u',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/fc2a56a5/tv-player-ias.vflset/tv-player-ias.js',"
b"+        u'qTKWg_Il804jd2kAC', u'OtUAm2W6gyzJjB9u',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/a74bf670/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'hQP7k1hA22OrNTnq',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/6275f73c/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'-I03XF0iyf6I_X0A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/20c72c18/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'-I03XF0iyf6I_X0A',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/9fe2e06e/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'6r5ekNIiEMPutZy',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/680f8c75/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'0ml9caTwpa55Jf',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/14397202/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'ozZFAN21okDdJTa',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/5dcb2c1f/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'p7iTbRZDYAF',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/a10d7fcc/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'9Zue7DDHJSD',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/8e20cb06/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'5-4tTneTROTpMzba',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/e12fbea4/player_ias_tce.vflset/en_US/base.js',"
b"+        u'kM5r52fugSZRAKHfo3', u'XkeRfXIPOkSwfg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/ef259203/player_ias_tce.vflset/en_US/base.js',"
b"+        u'rPqBC01nJpqhhi2iA2U', u'hY7dbiKFT51UIA',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/010fbc8d/player_es5.vflset/en_US/base.js',"
b"+        u'0hlOAlqjFszVvF4Z', u'R-H23bZGAsRFTg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/010fbc8d/player_es6.vflset/en_US/base.js',"
b"+        u'0hlOAlqjFszVvF4Z', u'R-H23bZGAsRFTg',"
b'+    ),'
b'+    ('
b"+        u'https://www.youtube.com/s/player/5ec65609/player_ias_tcc.vflset/en_US/base.js',"
b"+        u'6l5CTNx4AzIqH4MXM', u'NupToduxHBew1g',"
b'     ),'
b' ]'
b' '
b' '
b'-@is_download_test'
b' class TestPlayerInfo(unittest.TestCase):'
b'     def test_youtube_extract_player_info(self):'
b'         PLAYER_URLS = ('
b"-            ('https://www.youtube.com/s/player/4c3f79c5/player_ias.vflset/en_US/base.js', '4c3f79c5'),"
b"-            ('https://www.youtube.com/s/player/64dddad9/player_ias.vflset/en_US/base.js', '64dddad9'),"
b"-            ('https://www.youtube.com/s/player/64dddad9/player_ias.vflset/fr_FR/base.js', '64dddad9'),"
b"-            ('https://www.youtube.com/s/player/64dddad9/player-plasma-ias-phone-en_US.vflset/base.js', '64dddad9'),"
b"-            ('https://www.youtube.com/s/player/64dddad9/player-plasma-ias-phone-de_DE.vflset/base.js', '64dddad9'),"
b"-            ('https://www.youtube.com/s/player/64dddad9/player-plasma-ias-tablet-en_US.vflset/base.js', '64dddad9'),"
b"-            ('https://www.youtube.com/s/player/e7567ecf/player_ias_tce.vflset/en_US/base.js', 'e7567ecf'),"
b"-            ('https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js', '643afba4'),"
b"+            (u'https://www.youtube.com/s/player/4c3f79c5/player_ias.vflset/en_US/base.js', u'4c3f79c5'),"
b"+            (u'https://www.youtube.com/s/player/64dddad9/player_ias.vflset/en_US/base.js', u'64dddad9'),"
b"+            (u'https://www.youtube.com/s/player/64dddad9/player_ias.vflset/fr_FR/base.js', u'64dddad9'),"
b"+            (u'https://www.youtube.com/s/player/64dddad9/player-plasma-ias-phone-en_US.vflset/base.js', u'64dddad9'),"
b"+            (u'https://www.youtube.com/s/player/64dddad9/player-plasma-ias-phone-de_DE.vflset/base.js', u'64dddad9'),"
b"+            (u'https://www.youtube.com/s/player/64dddad9/player-plasma-ias-tablet-en_US.vflset/base.js', u'64dddad9'),"
b"+            (u'https://www.youtube.com/s/player/e7567ecf/player_ias_tce.vflset/en_US/base.js', u'e7567ecf'),"
b"+            (u'https://www.youtube.com/s/player/643afba4/tv-player-ias.vflset/tv-player-ias.js', u'643afba4'),"
b'             # obsolete'
b"-            ('https://www.youtube.com/yts/jsbin/player_ias-vfle4-e03/en_US/base.js', 'vfle4-e03'),"
b"-            ('https://www.youtube.com/yts/jsbin/player_ias-vfl49f_g4/en_US/base.js', 'vfl49f_g4'),"
b"-            ('https://www.youtube.com/yts/jsbin/player_ias-vflCPQUIL/en_US/base.js', 'vflCPQUIL'),"
b"-            ('https://www.youtube.com/yts/jsbin/player-vflzQZbt7/en_US/base.js', 'vflzQZbt7'),"
b"-            ('https://www.youtube.com/yts/jsbin/player-en_US-vflaxXRn1/base.js', 'vflaxXRn1'),"
b"-            ('https://s.ytimg.com/yts/jsbin/html5player-en_US-vflXGBaUN.js', 'vflXGBaUN'),"
b"-            ('https://s.ytimg.com/yts/jsbin/html5player-en_US-vflKjOTVq/html5player.js', 'vflKjOTVq'),"
b"+            (u'https://www.youtube.com/yts/jsbin/player_ias-vfle4-e03/en_US/base.js', u'vfle4-e03'),"
b"+            (u'https://www.youtube.com/yts/jsbin/player_ias-vfl49f_g4/en_US/base.js', u'vfl49f_g4'),"
b"+            (u'https://www.youtube.com/yts/jsbin/player_ias-vflCPQUIL/en_US/base.js', u'vflCPQUIL'),"
b"+            (u'https://www.youtube.com/yts/jsbin/player-vflzQZbt7/en_US/base.js', u'vflzQZbt7'),"
b"+            (u'https://www.youtube.com/yts/jsbin/player-en_US-vflaxXRn1/base.js', u'vflaxXRn1'),"
b"+            (u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflXGBaUN.js', u'vflXGBaUN'),"
b"+            (u'https://s.ytimg.com/yts/jsbin/html5player-en_US-vflKjOTVq/html5player.js', u'vflKjOTVq'),"
b'         )'
b'         for player_url, expected_player_id in PLAYER_URLS:'
b'             player_id = YoutubeIE._extract_player_info(player_url)'
b'             self.assertEqual(player_id, expected_player_id)'
b' '
b' '
b'-@is_download_test'
b'+TestPlayerInfo = is_download_test(TestPlayerInfo)'
b'+'
b' class TestSignature(unittest.TestCase):'
b'     def setUp(self):'
b'         TEST_DIR = os.path.dirname(os.path.abspath(__file__))'
b"-        self.TESTDATA_DIR = os.path.join(TEST_DIR, 'testdata/sigs')"
b"+        self.TESTDATA_DIR = os.path.join(TEST_DIR, u'testdata/sigs')"
b'         if not os.path.exists(self.TESTDATA_DIR):'
b'             os.mkdir(self.TESTDATA_DIR)'
b' '
b'@@ -447,19 +450,21 @@'
b'                 os.remove(f)'
b' '
b' '
b'+TestSignature = is_download_test(TestSignature)'
b'+'
b' def t_factory(name, sig_func, url_pattern):'
b'     def make_tfunc(url, sig_input, expected_sig):'
b'         m = url_pattern.match(url)'
b"         assert m, f'{url!r} should follow URL format'"
b"-        test_id = re.sub(r'[/.-]', '_', m.group('id') or m.group('compat_id'))"
b"+        test_id = re.sub(ur'[/.-]', u'_', m.group(u'id') or m.group(u'compat_id'))"
b' '
b'         def test_func(self):'
b"             basename = f'player-{test_id}.js'"
b'             fn = os.path.join(self.TESTDATA_DIR, basename)'
b' '
b'             if not os.path.exists(fn):'
b'-                urllib.request.urlretrieve(url, fn)'
b"-            with open(fn, encoding='utf-8') as testf:"
b'+                urllib.urlretrieve(url, fn)'
b"+            with open(fn, encoding=u'utf-8') as testf:"
b'                 jscode = testf.read()'
b'             self.assertEqual(sig_func(jscode, sig_input, url), expected_sig)'
b' '
b'@@ -471,7 +476,7 @@'
b' def signature(jscode, sig_input, player_url):'
b'     func = YoutubeIE(FakeYDL())._parse_sig_js(jscode, player_url)'
b'     src_sig = ('
b'-        str(string.printable[:sig_input])'
b'+        unicode(string.printable[:sig_input])'
b'         if isinstance(sig_input, int) else sig_input)'
b'     return func(src_sig)'
b' '
b'@@ -485,8 +490,8 @@'
b' '
b' '
b' make_sig_test = t_factory('
b"-    'signature', signature,"
b"-    re.compile(r'''(?x)"
b"+    u'signature', signature,"
b"+    re.compile(ur'''(?x)"
b'         .+(?:'
b'             /player/(?P<id>[a-zA-Z0-9_/.-]+)|'
b'             /html5player-(?:en_US-)?(?P<compat_id>[a-zA-Z0-9_-]+)(?:/watch_as3|/html5player)?'
b'@@ -495,10 +500,10 @@'
b'     make_sig_test(*test_spec)'
b' '
b' make_nsig_test = t_factory('
b"-    'nsig', n_sig, re.compile(r'.+/player/(?P<id>[a-zA-Z0-9_/.-]+)\\.js$'))"
b"+    u'nsig', n_sig, re.compile(ur'.+/player/(?P<id>[a-zA-Z0-9_/.-]+)\\.js$'))"
b' for test_spec in _NSIG_TESTS:'
b'     make_nsig_test(*test_spec)'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     unittest.main()'
