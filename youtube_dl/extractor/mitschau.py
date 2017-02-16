from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import ExtractorError

"""
<rss
    version="2.0"
    xmlns:media="http://search.yahoo.com/mrss/"
    xmlns:jwplayer="http://developer.longtailvideo.com/trac/wiki/FlashFormats">
  <channel>
    <item>
      <media:group>
        <media:content
            url="/lmu/mitschau/wise16/gvwl1_161220l.mp4"
            width="200"
            bitrate="150" />
        <media:content
            url="/lmu/mitschau/wise16/gvwl1_161220h.mp4"
            width="350"
            bitrate="500" />
        <media:content
            url="/lmu/mitschau/wise16/gvwl1_161220x.mp4"
            width="900"
            bitrate="1000" />
      </media:group>
      <jwplayer:streamer>
        rtmp://flash5.lrz.de:1935/Mitschau/
      </jwplayer:streamer>
    </item>
  </channel>
</rss>
"""

_ns = {
    'media': "http://search.yahoo.com/mrss/",
    'jwplayer': "http://developer.longtailvideo.com/trac/wiki/FlashFormats",
}

class MitschauIE(InfoExtractor):
    IE_NAME = 'videoonline.edu.lmu.de'
    _VALID_URL = r'https?://videoonline\.edu\.lmu\.de/(?:en|de)/node/(?P<id>[^/?#&]+)'

    _TESTS = [{
        'url': 'https://videoonline.edu.lmu.de/en/node/8171',
        'md5': '3a1eda8f3a29515d27f5adb967d7e740',
        'info_dict': {
            'id': '1839',
            'ext': 'mp4',
            'title': 'Introduction to Processor Design',
            'description': 'md5:df55f6d073d4ceae55aae6f2fd98a0ac',
            'thumbnail': r're:^https?://.*\.jpg$',
            'upload_date': '20131228',
            'timestamp': 1388188800,
            'duration': 3710,
        }
    }, {
        'url': 'https://media.ccc.de/v/32c3-7368-shopshifting#download',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        node_id = self._match_id(url)
        url = "https://videoonline.edu.lmu.de/en/node/%s" % node_id

        # get session cookie if needed
        if not any([x.startswith("SSESS")
                for x in self._get_cookies(url).keys()]):
            self.report_warning("getting cookies", node_id)
            self._download_webpage(url, node_id)

        xml = self._download_xml(url + "/bandwidth.rss", node_id)

        streamer = xml.findtext("channel/item/jwplayer:streamer",
                namespaces=_ns)
        if not streamer:
            raise ExtractorError("Malformed XML")

        formats = []
        for item in xml.findall(
                'channel/item/media:group/media:content', _ns):
            filename = item.attrib["url"][1:]
            formats.append({
                'url':   streamer + filename,
                'width': int(item.attrib["width"]),
                'tbr':   int(item.attrib["bitrate"]),

                # stupid shit because the RTMP url scheme is broken
                'app':   "Mitschau/",
                'play_path': "mp4:" + filename,

                # disable fast downloading
                'rtmp_real_time': True,
            })

        self._sort_formats(formats)

        return {
            'id': node_id,
            'title': "How should I know?",
            'formats': formats,
        }
