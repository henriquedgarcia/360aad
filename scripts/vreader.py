import os
import subprocess as sp
import time
import warnings
from collections import OrderedDict
from typing import Union

import numpy as np

_FFMPEG_PATH = "bin/"
_FFMPEG_APPLICATION = "ffmpeg.exe"
_FFPROBE_APPLICATION = "ffprobe.exe"
_FFMPEG_MAJOR_VERSION = "0"
_FFMPEG_MINOR_VERSION = "0"
_FFMPEG_PATCH_VERSION = "0"
_FFMPEG_SUPPORTED_DECODERS = []
_FFMPEG_SUPPORTED_ENCODERS = []
_HAS_FFMPEG = 0


def check_output(*popenargs, **kwargs) -> Union[bytes, str]:
    closeNULL = 0
    try:
        from subprocess import DEVNULL
        closeNULL = 0
    except ImportError:
        import os
        DEVNULL = open(os.devnull, 'wb')
        closeNULL = 1

    process = sp.Popen(stdout=sp.PIPE, stderr=DEVNULL, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()

    if closeNULL:
        DEVNULL.close()

    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = sp.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


def scan_ffmpeg():
    global _FFMPEG_MAJOR_VERSION
    global _FFMPEG_MINOR_VERSION
    global _FFMPEG_PATCH_VERSION
    global _FFMPEG_SUPPORTED_DECODERS
    global _FFMPEG_SUPPORTED_ENCODERS
    _FFMPEG_MAJOR_VERSION = "0"
    _FFMPEG_MINOR_VERSION = "0"
    _FFMPEG_PATCH_VERSION = "0"
    _FFMPEG_SUPPORTED_DECODERS = []
    _FFMPEG_SUPPORTED_ENCODERS = []
    try:
        # grab program version string
        version = check_output([os.path.join(_FFMPEG_PATH, _FFMPEG_APPLICATION), "-version"])
        # only parse the first line returned
        firstline = version.split(b'\n')[0]

        # the 3rd element in this line is the version number
        version = firstline.split(b' ')[2].strip()
        versionparts = version.split(b'.')
        if version[0] == b'N':
            # this is the 'git' version of FFmpeg
            _FFMPEG_MAJOR_VERSION = version
        else:
            _FFMPEG_MAJOR_VERSION = versionparts[0]
            _FFMPEG_MINOR_VERSION = versionparts[1]
            if len(versionparts) > 2:
                _FFMPEG_PATCH_VERSION = versionparts[2]
    except:
        pass

    # decoders = []
    # encoders = []

    # try:
    #     extension_lst = check_output([_FFMPEG_PATH + "/ffmpeg", "-formats"])
    #     extension_lst = extension_lst.split(b'\n')
    #     # skip first line
    #     for item in extension_lst[4:]:
    #         parts = [x.strip() for x in item.split(b' ') if x]
    #         if len(parts) < 2:
    #             continue
    #         rule = parts[0]
    #         extension = parts[1]
    #         if b'D' in rule:
    #             for item in extension.split(b","):
    #                 decoders.append(item)
    #         if b'E' in rule:
    #             for item in extension.split(b","):
    #                 encoders.append(item)
    # except:
    #     pass

    # try:
    #     for enc in encoders:
    #         extension_lst = check_output([_FFMPEG_PATH + "/ffmpeg", "-v", "1", "-h", "muxer="+str(enc)])
    #         csvstring = ""
    #         for line in extension_lst.split('\n'):
    #             if "Common extensions:" in line:
    #                 csvstring = line.replace("Common extensions:", "").replace(".", "").strip()
    #                 break
    #         if csvstring == "":
    #             continue
    #         csvlist = csvstring.split(',')
    #         for listitem in csvlist:
    #             _FFMPEG_SUPPORTED_ENCODERS.append(b"." + listitem)
    #     for enc in encoders:
    #         extension_lst = check_output([_FFMPEG_PATH + "/ffmpeg", "-v", "1", "-h", "demuxer="+str(enc)])
    #         csvstring = ""
    #         for line in extension_lst.split('\n'):
    #             if "Common extensions:" in line:
    #                 csvstring = line.replace("Common extensions:", "").replace(".", "").strip()
    #                 break
    #         if csvstring == "":
    #             continue
    #         csvlist = csvstring.split(',')
    #         for listitem in csvlist:
    #             _FFMPEG_SUPPORTED_ENCODERS.append(b"." + listitem)

    #     _FFMPEG_SUPPORTED_ENCODERS = np.unique(_FFMPEG_SUPPORTED_ENCODERS)
    # except:
    #     pass

    # try:
    #     for dec in decoders:
    #         extension_lst = check_output([_FFMPEG_PATH + "/ffmpeg", "-v", "1", "-h", "muxer="+str(dec)])
    #         csvstring = ""
    #         for line in extension_lst.split('\n'):
    #             if "Common extensions:" in line:
    #                 csvstring = line.replace("Common extensions:", "").replace(".", "").strip()
    #                 break
    #         if csvstring == "":
    #             continue
    #         csvlist = csvstring.split(',')
    #         for listitem in csvlist:
    #             _FFMPEG_SUPPORTED_DECODERS.append(b"." + listitem)
    #     for dec in decoders:
    #         extension_lst = check_output([_FFMPEG_PATH + "/ffmpeg", "-v", "1", "-h", "demuxer="+str(dec)])
    #         csvstring = ""
    #         for line in extension_lst.split('\n'):
    #             if "Common extensions:" in line:
    #                 csvstring = line.replace("Common extensions:", "").replace(".", "").strip()
    #                 break
    #         if csvstring == "":
    #             continue
    #         csvlist = csvstring.split(',')
    #         for listitem in csvlist:
    #             _FFMPEG_SUPPORTED_DECODERS.append(b"." + listitem)

    #     _FFMPEG_SUPPORTED_DECODERS = np.unique(_FFMPEG_SUPPORTED_DECODERS)
    # except:
    #     pass

    # by running the above code block, the bottom arrays are populated
    # output staticly provided for speed concerns
    _FFMPEG_SUPPORTED_DECODERS = [
        b'.264', b'.265', b'.302', b'.3g2', b'.3gp', b'.722', b'.aa', b'.aa3', b'.aac', b'.ac3',
        b'.acm', b'.adf', b'.adp', b'.ads', b'.adx', b'.aea', b'.afc', b'.aif', b'.aifc', b'.aiff',
        b'.al', b'.amr', b'.ans', b'.ape', b'.apl', b'.apng', b'.aqt', b'.art', b'.asc', b'.asf',
        b'.ass', b'.ast', b'.au', b'.avc', b'.avi', b'.avr', b'.bcstm', b'.bfstm', b'.bin', b'.bit',
        b'.bmp', b'.bmv', b'.brstm', b'.caf', b'.cavs', b'.cdata', b'.cdg', b'.cdxl', b'.cgi',
        b'.cif', b'.daud', b'.dav', b'.dif', b'.diz', b'.dnxhd', b'.dpx', b'.drc', b'.dss', b'.dtk', b'.dts',
        b'.dtshd', b'.dv', b'.eac3', b'.fap', b'.ffm', b'.ffmeta', b'.flac', b'.flm', b'.flv',
        b'.fsb', b'.g722', b'.g723_1', b'.g729', b'.genh', b'.gif', b'.gsm', b'.gxf', b'.h261',
        b'.h263', b'.h264', b'.h265', b'.h26l', b'.hevc', b'.ice', b'.ico', b'.idf', b'.idx', b'.im1',
        b'.im24', b'.im8', b'.ircam', b'.ivf', b'.ivr', b'.j2c', b'.j2k', b'.jls', b'.jp2', b'.jpeg',
        b'.jpg', b'.js', b'.jss', b'.lbc', b'.ljpg', b'.lrc', b'.lvf', b'.m2a', b'.m2t', b'.m2ts',
        b'.m3u8', b'.m4a', b'.m4v', b'.mac', b'.mj2', b'.mjpeg', b'.mjpg', b'.mk3d', b'.mka', b'.mks',
        b'.mkv', b'.mlp', b'.mmf', b'.mov', b'.mp2', b'.mp3', b'.mp4', b'.mpa', b'.mpc', b'.mpeg',
        b'.mpg', b'.mpl2', b'.mpo', b'.msf', b'.mts', b'.mvi', b'.mxf', b'.mxg', b'.nfo', b'.nist',
        b'.nut', b'.ogg', b'.ogv', b'.oma', b'.omg', b'.paf', b'.pam', b'.pbm', b'.pcx', b'.pgm',
        b'.pgmyuv', b'.pix', b'.pjs', b'.png', b'.ppm', b'.pvf', b'.qcif', b'.ra', b'.ras', b'.rco',
        b'.rcv', b'.rgb', b'.rm', b'.roq', b'.rs', b'.rsd', b'.rso', b'.rt', b'.sami', b'.sb', b'.sbg',
        b'.sdr2', b'.sf', b'.sgi', b'.shn', b'.sln', b'.smi', b'.son', b'.sox', b'.spdif', b'.sph',
        b'.srt', b'.ss2', b'.ssa', b'.stl', b'.str', b'.sub', b'.sun', b'.sunras', b'.sup', b'.svag',
        b'.sw', b'.swf', b'.tak', b'.tco', b'.tga', b'.thd', b'.tif', b'.tiff', b'.ts', b'.tta',
        b'.txt', b'.ub', b'.ul', b'.uw', b'.v', b'.v210', b'.vag', b'.vb', b'.vc1', b'.viv', b'.voc',
        b'.vpk', b'.vqe', b'.vqf', b'.vql', b'.vt', b'.vtt', b'.w64', b'.wav', b'.webm', b'.wma',
        b'.wmv', b'.wtv', b'.wv', b'.xbm', b'.xface', b'.xl', b'.xml', b'.xvag', b'.xwd', b'.y',
        b'.y4m', b'.yop', b'.yuv', b'.yuv10',

        # extra extensions that are known container formats
        b'.raw',
        b'.iso'
        ]

    _FFMPEG_SUPPORTED_ENCODERS = [
        b'., A64', b'.264', b'.265', b'.302', b'.3g2', b'.3gp', b'.722', b'.a64', b'.aa3', b'.aac',
        b'.ac3', b'.adts', b'.adx', b'.afc', b'.aif', b'.aifc', b'.aiff', b'.al', b'.amr', b'.apng',
        b'.asf', b'.ass', b'.ast', b'.au', b'.avc', b'.avi', b'.bit', b'.bmp', b'.caf', b'.cavs',
        b'.chk', b'.cif', b'.daud', b'.dav', b'.dif', b'.dnxhd', b'.dpx', b'.drc', b'.dts', b'.dv', b'.dvd',
        b'.eac3', b'.f4v', b'.ffm', b'.ffmeta', b'.flac', b'.flm', b'.flv', b'.g722', b'.g723_1',
        b'.gif', b'.gxf', b'.h261', b'.h263', b'.h264', b'.h265', b'.h26l', b'.hevc', b'.ico',
        b'.im1', b'.im24', b'.im8', b'.ircam', b'.isma', b'.ismv', b'.ivf', b'.j2c', b'.j2k', b'.jls',
        b'.jp2', b'.jpeg', b'.jpg', b'.js', b'.jss', b'.latm', b'.lbc', b'.ljpg', b'.loas', b'.lrc',
        b'.m1v', b'.m2a', b'.m2t', b'.m2ts', b'.m2v', b'.m3u8', b'.m4a', b'.m4v', b'.mj2', b'.mjpeg',
        b'.mjpg', b'.mk3d', b'.mka', b'.mks', b'.mkv', b'.mlp', b'.mmf', b'.mov', b'.mp2', b'.mp3',
        b'.mp4', b'.mpa', b'.mpeg', b'.mpg', b'.mpo', b'.mts', b'.mxf', b'.nut', b'.oga', b'.ogg',
        b'.ogv', b'.oma', b'.omg', b'.opus', b'.pam', b'.pbm', b'.pcx', b'.pgm', b'.pgmyuv', b'.pix',
        b'.png', b'.ppm', b'.psp', b'.qcif', b'.ra', b'.ras', b'.rco', b'.rcv', b'.rgb', b'.rm',
        b'.roq', b'.rs', b'.rso', b'.sb', b'.sf', b'.sgi', b'.sox', b'.spdif', b'.spx', b'.srt',
        b'.ssa', b'.sub', b'.sun', b'.sunras', b'.sw', b'.swf', b'.tco', b'.tga', b'.thd', b'.tif',
        b'.tiff', b'.ts', b'.ub', b'.ul', b'.uw', b'.vc1', b'.vob', b'.voc', b'.vtt', b'.w64', b'.wav',
        b'.webm', b'.webp', b'.wma', b'.wmv', b'.wtv', b'.wv', b'.xbm', b'.xface', b'.xml', b'.xwd',
        b'.y', b'.y4m', b'.yuv',

        # extra extensions that are known container formats
        b'.raw'
        ]


def setFFmpegPath(path):
    """ Sets up the path to the directory containing both ffmpeg and ffprobe

        Use this function for to specify specific system installs of FFmpeg. All
        calls to ffmpeg and ffprobe will use this path as a prefix.

        Parameters
        ----------
        path : string
            Path to directory containing ffmpeg and ffprobe

        Returns
        -------
        none

    """
    global _FFMPEG_PATH
    global _HAS_FFMPEG
    _FFMPEG_PATH = path

    # check to see if the executables actually exist on these paths
    if os.path.isfile(os.path.join(_FFMPEG_PATH, _FFMPEG_APPLICATION)) and os.path.isfile(os.path.join(_FFMPEG_PATH, _FFPROBE_APPLICATION)):
        _HAS_FFMPEG = 1
    else:
        warnings.warn("ffmpeg/ffprobe not found in path: " + str(path), UserWarning)
        _HAS_FFMPEG = 0
        global _FFMPEG_MAJOR_VERSION
        global _FFMPEG_MINOR_VERSION
        global _FFMPEG_PATCH_VERSION
        _FFMPEG_MAJOR_VERSION = "0"
        _FFMPEG_MINOR_VERSION = "0"
        _FFMPEG_PATCH_VERSION = "0"
        return

    # reload version from new path
    scan_ffmpeg()


setFFmpegPath(_FFMPEG_PATH)

bpplut = {"yuv420p": [3, 12], "yuyv422": [3, 16], "rgb24": [3, 24], "bgr24": [3, 24], "yuv422p": [3, 16], "yuv444p": [3, 24], "yuv410p": [3, 9], "yuv411p": [3, 12], "gray": [1, 8],
          "monow": [1, 1], "monob": [1, 1], "pal8": [1, 8], "yuvj420p": [3, 12], "yuvj422p": [3, 16], "yuvj444p": [3, 24], "xvmcmc": [0, 0], "xvmcidct": [0, 0], "uyvy422": [3, 16],
          "uyyvyy411": [3, 12], "bgr8": [3, 8], "bgr4": [3, 4], "bgr4_byte": [3, 4], "rgb8": [3, 8], "rgb4": [3, 4], "rgb4_byte": [3, 4], "nv12": [3, 12], "nv21": [3, 12],
          "argb": [4, 32], "rgba": [4, 32], "abgr": [4, 32], "bgra": [4, 32], "gray16be": [1, 16], "gray16le": [1, 16], "yuv440p": [3, 16], "yuvj440p": [3, 16],
          "yuva420p": [4, 20], "vdpau_h264": [0, 0], "vdpau_mpeg1": [0, 0], "vdpau_mpeg2": [0, 0], "vdpau_wmv3": [0, 0], "vdpau_vc1": [0, 0], "rgb48be": [3, 48],
          "rgb48le": [3, 48], "rgb565be": [3, 16], "rgb565le": [3, 16], "rgb555be": [3, 15], "rgb555le": [3, 15], "bgr565be": [3, 16], "bgr565le": [3, 16], "bgr555be": [3, 15],
          "bgr555le": [3, 15], "vaapi_moco": [0, 0], "vaapi_idct": [0, 0], "vaapi_vld": [0, 0], "yuv420p16le": [3, 24], "yuv420p16be": [3, 24], "yuv422p16le": [3, 32],
          "yuv422p16be": [3, 32], "yuv444p16le": [3, 48], "yuv444p16be": [3, 48], "vdpau_mpeg4": [0, 0], "dxva2_vld": [0, 0], "rgb444le": [3, 12], "rgb444be": [3, 12],
          "bgr444le": [3, 12], "bgr444be": [3, 12], "ya8": [2, 16], "bgr48be": [3, 48], "bgr48le": [3, 48], "yuv420p9be": [3, 13], "yuv420p9le": [3, 13], "yuv420p10be": [3, 15],
          "yuv420p10le": [3, 15], "yuv422p10be": [3, 20], "yuv422p10le": [3, 20], "yuv444p9be": [3, 27], "yuv444p9le": [3, 27], "yuv444p10be": [3, 30], "yuv444p10le": [3, 30],
          "yuv422p9be": [3, 18], "yuv422p9le": [3, 18], "vda_vld": [0, 0], "gbrp": [3, 24], "gbrp9be": [3, 27], "gbrp9le": [3, 27], "gbrp10be": [3, 30], "gbrp10le": [3, 30],
          "gbrp16be": [3, 48], "gbrp16le": [3, 48], "yuva420p9be": [4, 22], "yuva420p9le": [4, 22], "yuva422p9be": [4, 27], "yuva422p9le": [4, 27], "yuva444p9be": [4, 36],
          "yuva444p9le": [4, 36], "yuva420p10be": [4, 25], "yuva420p10le": [4, 25], "yuva422p10be": [4, 30], "yuva422p10le": [4, 30], "yuva444p10be": [4, 40],
          "yuva444p10le": [4, 40], "yuva420p16be": [4, 40], "yuva420p16le": [4, 40], "yuva422p16be": [4, 48], "yuva422p16le": [4, 48], "yuva444p16be": [4, 64],
          "yuva444p16le": [4, 64], "vdpau": [0, 0], "xyz12le": [3, 36], "xyz12be": [3, 36], "nv16": [3, 16], "nv20le": [3, 20], "nv20be": [3, 20], "yvyu422": [3, 16],
          "vda": [0, 0], "ya16be": [2, 32], "ya16le": [2, 32], "qsv": [0, 0], "mmal": [0, 0], "d3d11va_vld": [0, 0], "rgba64be": [4, 64], "rgba64le": [4, 64], "bgra64be": [4, 64],
          "bgra64le": [4, 64], "0rgb": [3, 24], "rgb0": [3, 24], "0bgr": [3, 24], "bgr0": [3, 24], "yuva444p": [4, 32], "yuva422p": [4, 24], "yuv420p12be": [3, 18],
          "yuv420p12le": [3, 18], "yuv420p14be": [3, 21], "yuv420p14le": [3, 21], "yuv422p12be": [3, 24], "yuv422p12le": [3, 24], "yuv422p14be": [3, 28], "yuv422p14le": [3, 28],
          "yuv444p12be": [3, 36], "yuv444p12le": [3, 36], "yuv444p14be": [3, 42], "yuv444p14le": [3, 42], "gbrp12be": [3, 36], "gbrp12le": [3, 36], "gbrp14be": [3, 42],
          "gbrp14le": [3, 42], "gbrap": [4, 32], "gbrap16be": [4, 64], "gbrap16le": [4, 64], "yuvj411p": [3, 12], "bayer_bggr8": [3, 8], "bayer_rggb8": [3, 8],
          "bayer_gbrg8": [3, 8], "bayer_grbg8": [3, 8], "bayer_bggr16le": [3, 16], "bayer_bggr16be": [3, 16], "bayer_rggb16le": [3, 16], "bayer_rggb16be": [3, 16],
          "bayer_gbrg16le": [3, 16], "bayer_gbrg16be": [3, 16], "bayer_grbg16le": [3, 16], "bayer_grbg16be": [3, 16], "yuv440p10le": [3, 20], "yuv440p10be": [3, 20],
          "yuv440p12le": [3, 24], "yuv440p12be": [3, 24], "ayuv64le": [4, 64], "ayuv64be": [4, 64], "videotoolbox_vld": [0, 0]}
from xml.parsers import expat


class VideoReaderAbstract(object):
    """Reads frames
    """

    INFO_AVERAGE_FRAMERATE = None  # "avg_frame_rate"
    INFO_WIDTH = None  # "width"
    INFO_HEIGHT = None  # "height"
    INFO_PIX_FMT = None  # "pix_fmt"
    INFO_DURATION = None  # "duration"
    INFO_NB_FRAMES = None  # "nb_frames"
    DEFAULT_FRAMERATE = 25.
    DEFAULT_INPUT_PIX_FMT = "yuvj444p"
    OUTPUT_METHOD = None  # "rawvideo"
    probeInfo: dict

    def __init__(self, filename, inputdict=None, outputdict=None, verbosity=0):
        """Initializes FFmpeg in reading mode with the given parameters

        During initialization, additional parameters about the video file
        are parsed using :func:`skvideo.io.ffprobe`. Then FFmpeg is launched
        as a subprocess. Parameters passed into inputdict are parsed and
        used to set as internal variables about the video. If the parameter,
        such as "Height" is not found in the inputdict, it is found through
        scanning the file's header information. If not in the header, ffprobe
        is used to decode the file to determine the information. In the case
        that the information is not supplied and connot be inferred from the
        input file, a ValueError exception is thrown.

        Parameters
        ----------
        filename : string
            Video file path

        inputdict : dict
            Input dictionary parameters, i.e. how to interpret the input file.

        outputdict : dict
            Output dictionary parameters, i.e. how to encode the data
            when sending back to the python process.

        Returns
        -------
        none

        """
        # check if FFMPEG exists in the path
        self._proc = None
        assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."

        self._filename = filename
        self.verbosity = verbosity

        if not inputdict:
            inputdict = {}

        if not outputdict:
            outputdict = {}

        # General information
        _, self.extension = os.path.splitext(filename)
        self.size = os.path.getsize(filename)
        self.probeInfo = self._probe()

        # smartphone video data is weird
        self.rotationAngle = '0'  # specific FFMPEG

        viddict = {}
        if "video" in self.probeInfo:
            viddict = self.probeInfo["video"]

        self.inputfps = -1
        if ("-r" in inputdict):
            self.inputfps = int(inputdict["-r"])
        elif self.INFO_AVERAGE_FRAMERATE in viddict:
            # check for the slash
            frtxt = viddict[self.INFO_AVERAGE_FRAMERATE]
            parts = frtxt.split('/')
            if len(parts) > 1:
                if float(parts[1]) == 0.:
                    self.inputfps = self.DEFAULT_FRAMERATE
                else:
                    self.inputfps = float(parts[0]) / float(parts[1])
            else:
                self.inputfps = float(frtxt)
        else:
            self.inputfps = self.DEFAULT_FRAMERATE

        # check for transposition tag
        if ('tag' in viddict):
            tagdata = viddict['tag']
            if not isinstance(tagdata, list):
                tagdata = [tagdata]

            for tags in tagdata:
                if tags['@key'] == 'rotate':
                    self.rotationAngle = tags['@value']

        # if we don't have width or height at all, raise exception
        if ("-s" in inputdict):
            widthheight = inputdict["-s"].split('x')
            self.inputwidth = int(widthheight[0])
            self.inputheight = int(widthheight[1])
        elif ((self.INFO_WIDTH in viddict) and (self.INFO_HEIGHT in viddict)):
            self.inputwidth = int(viddict[self.INFO_WIDTH])
            self.inputheight = int(viddict[self.INFO_HEIGHT])
        else:
            raise ValueError(
                "No way to determine width or height from video. Need `-s` in `inputdict`. Consult documentation on I/O.")

        # smartphone recordings seem to store data about rotations
        # in tag format. Just swap the width and height
        if self.rotationAngle == '90' or self.rotationAngle == '270':
            self.inputwidth, self.inputheight = self.inputheight, self.inputwidth

        self.bpp = -1  # bits per pixel
        self.pix_fmt = ""
        # completely unsure of this:
        if ("-pix_fmt" in inputdict):
            self.pix_fmt = inputdict["-pix_fmt"]
        elif (self.INFO_PIX_FMT in viddict):
            # parse this bpp
            self.pix_fmt = viddict[self.INFO_PIX_FMT]
        else:
            self.pix_fmt = self.DEFAULT_INPUT_PIX_FMT
            if verbosity != 0:
                warnings.warn("No input color space detected. Assuming {}.".format(self.DEFAULT_INPUT_PIX_FMT),
                              UserWarning)

        self.inputdepth = int(bpplut[self.pix_fmt][0])
        self.bpp = int(bpplut[self.pix_fmt][1])

        israw = str.encode(self.extension) in [b".raw", b".yuv"]
        iswebcam = not os.path.isfile(filename)

        if ("-vframes" in outputdict):
            self.inputframenum = int(outputdict["-vframes"])
        elif ("-r" in outputdict):
            inputfps = int(outputdict["-r"])

            inputduration = float(viddict[self.INFO_DURATION])

            self.inputframenum = int(round(inputfps * inputduration) + 1)
        elif (self.INFO_NB_FRAMES in viddict):
            self.inputframenum = int(viddict[self.INFO_NB_FRAMES])
        elif israw:
            # we can compute it based on the input size and color space
            self.inputframenum = int(self.size / (self.inputwidth * self.inputheight * (self.bpp / 8.0)))
        elif iswebcam:
            # webcam can stream frames endlessly, lets use the special default value of 0 to indicate that
            self.inputframenum = 0
        else:
            self.inputframenum = self._probCountFrames()
            if verbosity != 0:
                warnings.warn(
                    "Cannot determine frame count. Scanning input file, this is slow when repeated many times. Need `-vframes` in inputdict. Consult documentation on I/O.",
                    UserWarning)

        if israw or iswebcam:
            inputdict['-pix_fmt'] = self.pix_fmt
        else:
            decoders = self._getSupportedDecoders()
            if decoders != NotImplemented:
                # check that the extension makes sense
                assert str.encode(
                    self.extension).lower() in decoders, "Unknown decoder extension: " + self.extension.lower()

        if '-f' not in outputdict:
            outputdict['-f'] = self.OUTPUT_METHOD

        if '-pix_fmt' not in outputdict:
            outputdict['-pix_fmt'] = "rgb24"
        self.output_pix_fmt = outputdict['-pix_fmt']

        if '-s' in outputdict:
            widthheight = outputdict["-s"].split('x')
            self.outputwidth = int(widthheight[0])
            self.outputheight = int(widthheight[1])
        else:
            self.outputwidth = self.inputwidth
            self.outputheight = self.inputheight

        self.outputdepth = int(bpplut[outputdict['-pix_fmt']][0])
        self.outputbpp = int(bpplut[outputdict['-pix_fmt']][1])
        bitpercomponent = self.outputbpp // self.outputdepth
        if bitpercomponent == 8:
            self.dtype = np.dtype('u1')  # np.uint8
        elif bitpercomponent == 16:
            suffix = outputdict['-pix_fmt'][-2:]
            if suffix == 'le':
                self.dtype = np.dtype('<u2')
            elif suffix == 'be':
                self.dtype = np.dtype('>u2')
        else:
            raise ValueError(outputdict['-pix_fmt'] + 'is not a valid pix_fmt for numpy conversion')

        self._createProcess(inputdict, outputdict, verbosity)

    def __next__(self):
        return next(self.nextFrame())

    def __iter__(self):
        for frame in self.nextFrame():
            yield frame

    def _createProcess(self, inputdict, outputdict, verbosity):
        pass

    def _probCountFrames(self):
        return NotImplemented

    def _probe(self) -> dict:
        pass

    def _getSupportedDecoders(self):
        return NotImplemented

    def _dict2Args(self, dict):
        args = []
        for key in dict.categories():
            args.append(key)
            args.append(dict[key])
        return args

    def getShape(self):
        """Returns a tuple (T, M, N, C)

        Returns the video shape in number of frames, height, width, and channels per pixel.
        """

        return self.inputframenum, self.outputheight, self.outputwidth, self.outputdepth

    def close(self):
        if self._proc is not None and self._proc.poll() is None:
            self._proc.stdin.close()
            self._proc.stdout.close()
            self._proc.stderr.close()
            self._terminate(0.2)
        self._proc = None

    def _terminate(self, timeout=1.0):
        """ Terminate the sub process.
        """
        # Check
        if self._proc is None:  # pragma: no cover
            return  # no process
        if self._proc.poll() is not None:
            return  # process already dead
        # Terminate process
        self._proc.terminate()
        # Wait for it to close (but do not get stuck)
        etime = time.time() + timeout
        while time.time() < etime:
            time.sleep(0.01)
            if self._proc.poll() is not None:
                break

    def _read_frame_data(self):
        # Init and check
        framesize = self.outputdepth * self.outputwidth * self.outputheight
        assert self._proc is not None

        try:
            # Read framesize bytes
            arr = np.frombuffer(self._proc.stdout.read(framesize * self.dtype.itemsize), dtype=self.dtype)
            if len(arr) != framesize:
                return np.array([])
            # assert len(arr) == framesize
        except Exception as err:
            self._terminate()
            err1 = str(err)
            raise RuntimeError("%s" % (err1,))
        return arr

    def _readFrame(self):
        # Read and convert to numpy array
        frame = self._read_frame_data()
        if len(frame) == 0:
            return frame

        if self.output_pix_fmt == 'rgb24':
            self._lastread = frame.reshape((self.outputheight, self.outputwidth, self.outputdepth))
        elif self.output_pix_fmt.startswith('yuv444p') or self.output_pix_fmt.startswith(
                'yuvj444p') or self.output_pix_fmt.startswith('yuva444p'):
            self._lastread = frame.reshape((self.outputdepth, self.outputheight, self.outputwidth)).transpose((1, 2, 0))
        else:
            if self.verbosity > 0:
                warnings.warn(
                    'Unsupported reshaping from raw buffer to images frames  for format {:}. Assuming HEIGHTxWIDTHxCOLOR'.format(
                        self.output_pix_fmt), UserWarning)
            self._lastread = frame.reshape((self.outputheight, self.outputwidth, self.outputdepth))

        return self._lastread

    inputframenum: int

    def nextFrame(self):
        """Yields frames using a generator

        Returns T ndarrays of size (M, N, C), where T is number of frames,
        M is height, N is width, and C is number of channels per pixel.

        """
        if self.inputframenum == 0:
            while True:
                frame = self._readFrame()
                if len(frame) == 0:
                    break
                yield frame
        else:
            for i in range(self.inputframenum):
                frame = self._readFrame()
                if len(frame) == 0:
                    break
                yield frame

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler(object):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True,
                 namespace_separator=':',
                 namespaces=None,
                 force_list=()):
        self.path = []
        self.stack = []
        self.data = []
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.force_list = force_list

    def _build_name(self, full_name):
        if not self.namespaces:
            return full_name
        i = full_name.rfind(self.namespace_separator)
        if i == -1:
            return full_name
        namespace, name = full_name[:i], full_name[i + 1:]
        short_namespace = self.namespaces.get(namespace, namespace)
        if not short_namespace:
            return name
        else:
            return self.namespace_separator.join((short_namespace, name))

    def _attrs_to_dict(self, attrs):
        if isinstance(attrs, dict):
            return attrs
        return self.dict_constructor(zip(attrs[0::2], attrs[1::2]))

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        attrs = self._attrs_to_dict(attrs)
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(
                    (self.attr_prefix + self._build_name(key), value)
                    for (key, value) in attrs.items())
            else:
                attrs = None
            self.item = attrs or None
            self.data = []

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = (None if not self.data
                        else self.cdata_separator.join(self.data))

            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            data = (None if not self.data
                    else self.cdata_separator.join(self.data))
            item = self.item
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = None
            self.data = []
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = [data]
        else:
            self.data.append(data)

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            if key in self.force_list:
                item[key] = [data]
            else:
                item[key] = data
        return item


_unicode = str


def xmltodictparser(xml_input, encoding=None, expat=expat, process_namespaces=False,
                    namespace_separator=':', **kwargs):
    handler = _DictSAXHandler(namespace_separator=namespace_separator,
                              **kwargs)
    if isinstance(xml_input, _unicode):
        if not encoding:
            encoding = 'utf-8'
        xml_input = xml_input.encode(encoding)
    if not process_namespaces:
        namespace_separator = None
    parser = expat.ParserCreate(
        encoding,
        namespace_separator
        )
    try:
        parser.ordered_attributes = True
    except AttributeError:
        # Jython's expat does not support ordered_attributes
        pass
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    try:
        parser.ParseFile(xml_input)
    except (TypeError, AttributeError):
        parser.Parse(xml_input, True)
    return handler.item


def ffprobe(filename):
    """get metadata by using ffprobe

    Checks the output of ffprobe on the desired video
    file. MetaData is then parsed into a dictionary.

    Parameters
    ----------
    filename : string
        Path to the video file

    Returns
    -------
    metaDict : dict
       Dictionary containing all header-based information
       about the passed-in source video.

    """
    # check if FFMPEG exists in the path
    assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."

    try:
        command = [_FFMPEG_PATH + "/" + _FFPROBE_APPLICATION, "-v", "error", "-show_streams", "-print_format", "xml", filename]

        # simply get std output
        xml = check_output(command)

        d = xmltodictparser(xml)["ffprobe"]

        d = d["streams"]

        # import json
        # print json.dumps(d, indent = 4)
        # exit(0)

        # check type
        streamsbytype = {}
        if type(d["stream"]) is list:
            # go through streams
            for stream in d["stream"]:
                streamsbytype[stream["@codec_type"].lower()] = stream
        else:
            streamsbytype[d["stream"]["@codec_type"].lower()] = d["stream"]

        return streamsbytype
    except:
        return {}


class FFmpegReader(VideoReaderAbstract):
    """Reads frames using FFmpeg

    Using FFmpeg as a backend, this class
    provides sane initializations meant to
    handle the default case well.

    """

    INFO_AVERAGE_FRAMERATE = "@r_frame_rate"
    INFO_WIDTH = "@width"
    INFO_HEIGHT = "@height"
    INFO_PIX_FMT = "@pix_fmt"
    INFO_DURATION = "@duration"
    INFO_NB_FRAMES = "@nb_frames"
    OUTPUT_METHOD = "image2pipe"

    def __init__(self, *args, **kwargs):

        """Initializes FFmpeg in reading mode with the given parameters

        During initialization, additional parameters about the video file
        are parsed using :func:`skvideo.io.ffprobe`. Then FFmpeg is launched
        as a subprocess. Parameters passed into inputdict are parsed and
        used to set as internal variables about the video. If the parameter,
        such as "Height" is not found in the inputdict, it is found through
        scanning the file's header information. If not in the header, ffprobe
        is used to decode the file to determine the information. In the case
        that the information is not supplied and connot be inferred from the
        input file, a ValueError exception is thrown.

        Parameters
        ----------
        filename : string
            Video file path

        inputdict : dict
            Input dictionary parameters, i.e. how to interpret the input file.

        outputdict : dict
            Output dictionary parameters, i.e. how to encode the data
            when sending back to the python process.

        Returns
        -------
        none

        """
        # check if FFMPEG exists in the path
        self._proc = None
        assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."

        self._filename = filename
        self.verbosity = verbosity

        if not inputdict:
            inputdict = {}

        if not outputdict:
            outputdict = {}

        # General information
        _, self.extension = os.path.splitext(filename)
        self.size = os.path.getsize(filename)
        self.probeInfo = self._probe()

        # smartphone video data is weird
        self.rotationAngle = '0'  # specific FFMPEG

        viddict = {}
        if "video" in self.probeInfo:
            viddict = self.probeInfo["video"]

        self.inputfps = -1
        if ("-r" in inputdict):
            self.inputfps = int(inputdict["-r"])
        elif self.INFO_AVERAGE_FRAMERATE in viddict:
            # check for the slash
            frtxt = viddict[self.INFO_AVERAGE_FRAMERATE]
            parts = frtxt.split('/')
            if len(parts) > 1:
                if float(parts[1]) == 0.:
                    self.inputfps = self.DEFAULT_FRAMERATE
                else:
                    self.inputfps = float(parts[0]) / float(parts[1])
            else:
                self.inputfps = float(frtxt)
        else:
            self.inputfps = self.DEFAULT_FRAMERATE

        # check for transposition tag
        if ('tag' in viddict):
            tagdata = viddict['tag']
            if not isinstance(tagdata, list):
                tagdata = [tagdata]

            for tags in tagdata:
                if tags['@key'] == 'rotate':
                    self.rotationAngle = tags['@value']

        # if we don't have width or height at all, raise exception
        if ("-s" in inputdict):
            widthheight = inputdict["-s"].split('x')
            self.inputwidth = int(widthheight[0])
            self.inputheight = int(widthheight[1])
        elif ((self.INFO_WIDTH in viddict) and (self.INFO_HEIGHT in viddict)):
            self.inputwidth = int(viddict[self.INFO_WIDTH])
            self.inputheight = int(viddict[self.INFO_HEIGHT])
        else:
            raise ValueError(
                "No way to determine width or height from video. Need `-s` in `inputdict`. Consult documentation on I/O.")

        # smartphone recordings seem to store data about rotations
        # in tag format. Just swap the width and height
        if self.rotationAngle == '90' or self.rotationAngle == '270':
            self.inputwidth, self.inputheight = self.inputheight, self.inputwidth

        self.bpp = -1  # bits per pixel
        self.pix_fmt = ""
        # completely unsure of this:
        if ("-pix_fmt" in inputdict):
            self.pix_fmt = inputdict["-pix_fmt"]
        elif (self.INFO_PIX_FMT in viddict):
            # parse this bpp
            self.pix_fmt = viddict[self.INFO_PIX_FMT]
        else:
            self.pix_fmt = self.DEFAULT_INPUT_PIX_FMT
            if verbosity != 0:
                warnings.warn("No input color space detected. Assuming {}.".format(self.DEFAULT_INPUT_PIX_FMT),
                              UserWarning)

        self.inputdepth = int(bpplut[self.pix_fmt][0])
        self.bpp = int(bpplut[self.pix_fmt][1])

        israw = str.encode(self.extension) in [b".raw", b".yuv"]
        iswebcam = not os.path.isfile(filename)

        if ("-vframes" in outputdict):
            self.inputframenum = int(outputdict["-vframes"])
        elif ("-r" in outputdict):
            inputfps = int(outputdict["-r"])

            inputduration = float(viddict[self.INFO_DURATION])

            self.inputframenum = int(round(inputfps * inputduration) + 1)
        elif (self.INFO_NB_FRAMES in viddict):
            self.inputframenum = int(viddict[self.INFO_NB_FRAMES])
        elif israw:
            # we can compute it based on the input size and color space
            self.inputframenum = int(self.size / (self.inputwidth * self.inputheight * (self.bpp / 8.0)))
        elif iswebcam:
            # webcam can stream frames endlessly, lets use the special default value of 0 to indicate that
            self.inputframenum = 0
        else:
            self.inputframenum = self._probCountFrames()
            if verbosity != 0:
                warnings.warn(
                    "Cannot determine frame count. Scanning input file, this is slow when repeated many times. Need `-vframes` in inputdict. Consult documentation on I/O.",
                    UserWarning)

        if israw or iswebcam:
            inputdict['-pix_fmt'] = self.pix_fmt
        else:
            decoders = self._getSupportedDecoders()
            if decoders != NotImplemented:
                # check that the extension makes sense
                assert str.encode(
                    self.extension).lower() in decoders, "Unknown decoder extension: " + self.extension.lower()

        if '-f' not in outputdict:
            outputdict['-f'] = self.OUTPUT_METHOD

        if '-pix_fmt' not in outputdict:
            outputdict['-pix_fmt'] = "rgb24"
        self.output_pix_fmt = outputdict['-pix_fmt']

        if '-s' in outputdict:
            widthheight = outputdict["-s"].split('x')
            self.outputwidth = int(widthheight[0])
            self.outputheight = int(widthheight[1])
        else:
            self.outputwidth = self.inputwidth
            self.outputheight = self.inputheight

        self.outputdepth = int(bpplut[outputdict['-pix_fmt']][0])
        self.outputbpp = int(bpplut[outputdict['-pix_fmt']][1])
        bitpercomponent = self.outputbpp // self.outputdepth
        if bitpercomponent == 8:
            self.dtype = np.dtype('u1')  # np.uint8
        elif bitpercomponent == 16:
            suffix = outputdict['-pix_fmt'][-2:]
            if suffix == 'le':
                self.dtype = np.dtype('<u2')
            elif suffix == 'be':
                self.dtype = np.dtype('>u2')
        else:
            raise ValueError(outputdict['-pix_fmt'] + 'is not a valid pix_fmt for numpy conversion')

        self._createProcess(inputdict, outputdict, verbosity)


    def _createProcess(self, inputdict, outputdict, verbosity):
        if '-vcodec' not in outputdict:
            outputdict['-vcodec'] = "rawvideo"

        iargs = self._dict2Args(inputdict)
        oargs = self._dict2Args(outputdict)

        if verbosity > 0:
            cmd = [_FFMPEG_PATH + "/" + _FFMPEG_APPLICATION] + iargs + ['-i', self._filename] + oargs + ['-']
            print(cmd)
            self._proc = sp.Popen(cmd, stdin=sp.PIPE,
                                  stdout=sp.PIPE, stderr=None)
        else:
            cmd = [_FFMPEG_PATH + "/" + _FFMPEG_APPLICATION, "-nostats", "-loglevel", "0"] + iargs + ['-i',
                                                                                                      self._filename] + oargs + [
                      '-']
        self._proc = sp.Popen(cmd, stdin=sp.PIPE,
                              stdout=sp.PIPE, stderr=sp.PIPE)
        self._cmd = " ".join(cmd)

    def _probCountFrames(self):
        # open process, grabbing number of frames using ffprobe
        probecmd = [_FFMPEG_PATH + "/ffprobe"] + ["-v", "error", "-count_frames", "-select_streams", "v:0",
                                                  "-show_entries", "stream=nb_read_frames", "-of",
                                                  "default=nokey=1:noprint_wrappers=1", self._filename]
        return int(check_output(probecmd).decode().split('\n')[0])

    def _probe(self):
        return ffprobe(self._filename)

    def _getSupportedDecoders(self):
        return _FFMPEG_SUPPORTED_DECODERS


def vshape(videodata):
    """Standardizes the input data shape.

    Transforms video data into the standardized shape (T, M, N, C), where
    T is number of frames, M is height, N is width, and C is number of
    channels.

    Parameters
    ----------
    videodata : ndarray
        Input data of shape (T, M, N, C), (T, M, N), (M, N, C), or (M, N), where
        T is number of frames, M is height, N is width, and C is number of
        channels.

    Returns
    -------
    videodataout : ndarray
        Standardized version of videodata, shape (T, M, N, C)

    """
    import numpy as np
    if not isinstance(videodata, np.ndarray):
        videodata = np.array(videodata)

    if len(videodata.shape) == 2:
        a, b = videodata.shape
        return videodata.reshape(1, a, b, 1)
    elif len(videodata.shape) == 3:
        a, b, c = videodata.shape
        # check the last dimension small
        # interpret as color channel
        if c in [1, 2, 3, 4]:
            return videodata.reshape(1, a, b, c)
        else:
            return videodata.reshape(a, b, c, 1)
    elif len(videodata.shape) == 4:
        return videodata
    else:
        raise ValueError("Improper data input")


class VideoWriterAbstract(object):
    """Writes frames

    this class provides sane initializations for the default case.
    """
    NEED_RGB2GRAY_HACK = False
    DEFAULT_OUTPUT_PIX_FMT = "yuvj444p"

    def __init__(self, filename, inputdict=None, outputdict=None, verbosity=0):
        """Prepares parameters

        Does not instantiate the an FFmpeg subprocess, but simply
        prepares the required parameters.

        Parameters
        ----------
        filename : string
            Video file path for writing

        inputdict : dict
            Input dictionary parameters, i.e. how to interpret the data coming from python.

        outputdict : dict
            Output dictionary parameters, i.e. how to encode the data
            when writing to file.

        Returns
        -------
        none

        """
        self.DEVNULL = open(os.devnull, 'wb')

        filename = os.path.abspath(filename)
        _, self.extension = os.path.splitext(filename)

        # check that the extension makes sense
        encoders = self._getSupportedEncoders()
        if encoders != NotImplemented:
            assert str.encode(
                self.extension).lower() in encoders, "Unknown encoder extension: " + self.extension.lower()

        self._filename = filename
        basepath, _ = os.path.split(filename)

        # check to see if filename is a valid file location
        assert os.access(basepath, os.W_OK), "Cannot write to directory: " + basepath

        if not inputdict:
            inputdict = {}

        if not outputdict:
            outputdict = {}

        self.inputdict = inputdict
        self.outputdict = outputdict
        self.verbosity = verbosity

        if "-f" not in self.inputdict:
            self.inputdict["-f"] = "rawvideo"
        self.warmStarted = False

    def _warmStart(self, M, N, C, dtype):
        self.warmStarted = True

        if "-pix_fmt" not in self.inputdict:
            # check the number channels to guess
            if dtype.kind == 'u' and dtype.itemsize == 2:
                suffix = 'le' if dtype.byteorder else 'be'
                if C == 1:
                    if self.NEED_RGB2GRAY_HACK:
                        self.inputdict["-pix_fmt"] = "rgb48" + suffix
                        self.rgb2grayhack = True
                        C = 3
                    else:
                        self.inputdict["-pix_fmt"] = "gray16" + suffix
                elif C == 2:
                    self.inputdict["-pix_fmt"] = "ya16" + suffix
                elif C == 3:
                    self.inputdict["-pix_fmt"] = "rgb48" + suffix
                elif C == 4:
                    self.inputdict["-pix_fmt"] = "rgba64" + suffix
                else:
                    raise NotImplemented
            else:
                if C == 1:
                    if self.NEED_RGB2GRAY_HACK:
                        self.inputdict["-pix_fmt"] = "rgb24"
                        self.rgb2grayhack = True
                        C = 3
                    else:
                        self.inputdict["-pix_fmt"] = "gray"
                elif C == 2:
                    self.inputdict["-pix_fmt"] = "ya8"
                elif C == 3:
                    self.inputdict["-pix_fmt"] = "rgb24"
                elif C == 4:
                    self.inputdict["-pix_fmt"] = "rgba"
                else:
                    raise NotImplemented

        self.bpp = bpplut[self.inputdict["-pix_fmt"]][1]
        self.inputNumChannels = bpplut[self.inputdict["-pix_fmt"]][0]
        bitpercomponent = self.bpp // self.inputNumChannels
        if bitpercomponent == 8:
            self.dtype = np.dtype('u1')  # np.uint8
        elif bitpercomponent == 16:
            suffix = self.inputdict['-pix_fmt'][-2:]
            if suffix == 'le':
                self.dtype = np.dtype('<u2')
            elif suffix == 'be':
                self.dtype = np.dtype('>u2')
        else:
            raise ValueError(self.inputdict['-pix_fmt'] + 'is not a valid pix_fmt for numpy conversion')

        assert self.inputNumChannels == C, "Failed to pass the correct number of channels %d for the pixel format %s." % (
            self.inputNumChannels, self.inputdict["-pix_fmt"])

        if ("-s" in self.inputdict):
            widthheight = self.inputdict["-s"].split('x')
            self.inputwidth = int(widthheight[0])
            self.inputheight = int(widthheight[1])
        else:
            self.inputdict["-s"] = str(N) + "x" + str(M)
            self.inputwidth = N
            self.inputheight = M

        # prepare output parameters, if raw
        if self.extension == ".yuv":
            if "-pix_fmt" not in self.outputdict:
                self.outputdict["-pix_fmt"] = self.DEFAULT_OUTPUT_PIX_FMT
                if self.verbosity > 0:
                    warnings.warn("No output color space provided. Assuming {}.".format(self.DEFAULT_OUTPUT_PIX_FMT),
                                  UserWarning)

        self._createProcess(self.inputdict, self.outputdict, self.verbosity)

    def _createProcess(self, inputdict, outputdict, verbosity):
        pass

    def _prepareData(self, data):
        return data  # general case : do nothing

    _proc = None

    def close(self):
        """Closes the video and terminates FFmpeg process

        """
        if self._proc is None:  # pragma: no cover
            return  # no process
        if self._proc.poll() is not None:
            return  # process already dead
        if self._proc.stdin:
            self._proc.stdin.close()
        self._proc.wait()
        self._proc = None
        self.DEVNULL.close()

    def writeFrame(self, im):
        """Sends ndarray frames to FFmpeg

        """
        vid = vshape(im)
        T, M, N, C = vid.shape
        if not self.warmStarted:
            self._warmStart(M, N, C, im.dtype)

        vid = vid.clip(0, (1 << (self.dtype.itemsize << 3)) - 1).astype(self.dtype)
        vid = self._prepareData(vid)
        T, M, N, C = vid.shape  # in case of hack ine prepareData to change the image shape (gray2RGB in libAV for exemple)

        # check if we need to do some bit-plane swapping
        # for the raw data format
        if self.inputdict["-pix_fmt"].startswith('yuv444p') or self.inputdict["-pix_fmt"].startswith('yuvj444p') or \
                self.inputdict["-pix_fmt"].startswith('yuva444p'):
            vid = vid.transpose((0, 3, 1, 2))

        # Check size of image
        if M != self.inputheight or N != self.inputwidth:
            raise ValueError('All images in a movie should have same size')
        if C != self.inputNumChannels:
            raise ValueError('All images in a movie should have same '
                             'number of channels')

        assert self._proc is not None  # Check status

        # Write
        try:
            self._proc.stdin.write(vid.tostring())
        except IOError as e:
            # Show the command and stderr from pipe
            msg = '{0:}\n\nFFMPEG COMMAND:\n{1:}\n\nFFMPEG STDERR ' \
                  'OUTPUT:\n'.format(e, self._cmd)
            raise IOError(msg)

    def _getSupportedEncoders(self):
        return NotImplemented

    def _dict2Args(self, dict):
        args = []
        for key in dict.categories():
            args.append(key)
            args.append(dict[key])
        return args

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class FFmpegWriter(VideoWriterAbstract):
    """Writes frames using FFmpeg

    Using FFmpeg as a backend, this class
    provides sane initializations for the default case.
    """

    def __init__(self, *args, **kwargs):
        assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."
        super(FFmpegWriter, self).__init__(*args, **kwargs)

    def _getSupportedEncoders(self):
        return _FFMPEG_SUPPORTED_ENCODERS

    def _createProcess(self, inputdict, outputdict, verbosity):
        iargs = self._dict2Args(inputdict)
        oargs = self._dict2Args(outputdict)

        cmd = [_FFMPEG_PATH + "/" + _FFMPEG_APPLICATION, "-y"] + iargs + ["-i", "-"] + oargs + [self._filename]

        self._cmd = " ".join(cmd)

        # Launch process
        if self.verbosity > 0:
            print(self._cmd)
            self._proc = sp.Popen(cmd, stdin=sp.PIPE,
                                  stdout=sp.PIPE, stderr=None)
        else:
            self._proc = sp.Popen(cmd, stdin=sp.PIPE,
                                  stdout=self.DEVNULL, stderr=sp.STDOUT)
