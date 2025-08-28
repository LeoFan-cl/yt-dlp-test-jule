# flake8: noqa: F401
from __future__ import absolute_import

from .common import PostProcessor
from .embedthumbnail import EmbedThumbnailPP
from .exec import ExecAfterDownloadPP, ExecPP
from .ffmpeg import (
    FFmpegConcatPP,
    FFmpegCopyStreamPP,
    FFmpegEmbedSubtitlePP,
    FFmpegExtractAudioPP,
    FFmpegFixupDuplicateMoovPP,
    FFmpegFixupDurationPP,
    FFmpegFixupM3u8PP,
    FFmpegFixupM4aPP,
    FFmpegFixupStretchedPP,
    FFmpegFixupTimestampPP,
    FFmpegMergerPP,
    FFmpegMetadataPP,
    FFmpegPostProcessor,
    FFmpegSplitChaptersPP,
    FFmpegSubtitlesConvertorPP,
    FFmpegThumbnailsConvertorPP,
    FFmpegVideoConvertorPP,
    FFmpegVideoRemuxerPP,
)
from .metadataparser import (
    MetadataFromFieldPP,
    MetadataFromTitlePP,
    MetadataParserPP,
)
from .modify_chapters import ModifyChaptersPP
from .movefilesafterdownload import MoveFilesAfterDownloadPP
from .sponskrub import SponSkrubPP
from .sponsorblock import SponsorBlockPP
from .xattrpp import XAttrMetadataPP
from ..globals import plugin_pps, postprocessors
from ..plugins import PACKAGE_NAME, register_plugin_spec, PluginSpec
from ..utils import deprecation_warning

# __getattr__ is a Python 3.7+ feature.
# The original code used it to provide deprecation warnings for plugin imports.
# As a workaround for Python 2.7, we directly expose the plugin postprocessors
# as module attributes, sacrificing the deprecation warning.
for name, pp in plugin_pps.value.items():
    if name not in globals():
        globals()[name] = pp


def get_postprocessor(key):
    return postprocessors.value[key + 'PP']


register_plugin_spec(PluginSpec(
    module_name='postprocessor',
    suffix='PP',
    destination=postprocessors,
    plugin_destination=plugin_pps,
))

_default_pps = dict(
    (name, value)
    for name, value in globals().items()
    if name.endswith('PP') or name in ('FFmpegPostProcessor', 'PostProcessor')
)
postprocessors.value.update(_default_pps)

__all__ = list(_default_pps.keys())
