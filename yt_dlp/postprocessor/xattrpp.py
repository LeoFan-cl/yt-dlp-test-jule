from __future__ import absolute_import
import os
import sys

from .common import PostProcessor
from ..utils import (
    hyphenate_date,
    PostProcessingError,
    write_xattr,
    XAttrUnavailableError,
    XAttrMetadataError,
)


class XAttrMetadataPP(PostProcessor):
    u"""Set extended attributes on downloaded file (if xattr support is found)

    More info about extended attributes for media:
        http://freedesktop.org/wiki/CommonExtendedAttributes/
    This post-processor will write the following attributes:
    - user.xdg.referrer.url (URL of the downloaded file)
    - user.dublincore.title (Title of the video)
    - user.dublincore.date (Upload date)
    - user.dublincore.description (Description)
    - user.dublincore.contributor (Uploader)
    - user.dublincore.format (File format)
    - com.apple.metadata:kMDItemWhereFroms (URL of the downloaded file, for OS X)
    """

    XATTR_MAPPING = {
        u'user.xdg.referrer.url': u'webpage_url',
        u'user.dublincore.title': u'title',
        u'user.dublincore.date': u'upload_date',
        u'user.dublincore.contributor': u'uploader',
        u'user.dublincore.format': u'format',
        # We do this last because it may get us close to the xattr limits
        # (e.g., 4kB on ext4), and we don't want to have the other ones fail
        u'user.dublincore.description': u'description',
        # 'user.xdg.comment': 'description',
        u'com.apple.metadata:kMDItemWhereFroms': u'webpage_url',
    }

    APPLE_PLIST_TEMPLATE = u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<array>
    <string>%s</string>
</array>
</plist>'''

    def run(self, info):
        mtime = os.stat(info[u'filepath']).st_mtime
        self.to_screen('Writing metadata to file\'s xattrs')
        for xattrname, infoname in self.XATTR_MAPPING.items():
            try:
                value = info.get(infoname)
                if value:
                    if infoname == u'upload_date':
                        value = hyphenate_date(value)
                    elif xattrname == u'com.apple.metadata:kMDItemWhereFroms':
                        # Colon in xattr name throws errors on Windows/NTFS and Linux
                        if sys.platform != u'darwin':
                            continue
                        value = self.APPLE_PLIST_TEMPLATE % value
                    write_xattr(info[u'filepath'], xattrname, value.encode('utf-8'))

            except XAttrUnavailableError, e:
                raise PostProcessingError(unicode(e))
            except XAttrMetadataError, e:
                if e.reason == u'NO_SPACE':
                    self.report_warning(
                        u'There\'s no disk space left, disk quota exceeded or filesystem xattr limit exceeded. '
                        'Extended attribute "%s" was not written.' % xattrname)
                elif e.reason == u'VALUE_TOO_LONG':
                    self.report_warning('Unable to write extended attribute "%s" due to too long values.' % xattrname)
                else:
                    tip = (u'You need to use NTFS' if os.name == u'nt'
                           else u'You may have to enable them in your "/etc/fstab"')
                    raise PostProcessingError('This filesystem doesn\'t support extended attributes. %s' % tip)

        self.try_utime(info[u'filepath'], mtime, mtime)
        return [], info
