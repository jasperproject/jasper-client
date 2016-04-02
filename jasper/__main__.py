# -*- coding: utf-8 -*-
import sys
import logging
import argparse
import io
from . import application
from application import USE_STANDARD_MIC, USE_TEXT_MIC, USE_BATCH_MIC


def is_valid_file(parser, arg):

    try:
        fileid = io.open(arg, "r", encoding="utf-8")
    except IOError:
        parser.error("The file %s does not exist!" % arg)
    return fileid


def main(args=None):

    parser = argparse.ArgumentParser(description='Jasper Voice Control Center')
    parser.add_argument('--local', action='store_true',
                        help='Use text input instead of a real microphone')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug messages')
    list_info = parser.add_mutually_exclusive_group(required=False)
    list_info.add_argument('--list-plugins', action='store_true',
                           help='List plugins and exit')
    list_info.add_argument('--list-audio-devices', action='store_true',
                           help='List audio devices and exit')
    parser.add_argument('--batch', dest='batch_filename', metavar="FILE",
                        type=lambda x: is_valid_file(parser, x),
                        help='Batch mode using a text file with text commands \
                        or audio filenames at each line. Use # for comments.')
    p_args = parser.parse_args(args)

    print("*******************************************************")
    print("*             JASPER - THE TALKING COMPUTER           *")
    print("* (c) 2015 Shubhro Saha, Charlie Marsh & Jan Holthuis *")
    print("*******************************************************")

    # Set up logging
    logging.basicConfig(level=logging.DEBUG if p_args.debug else logging.INFO)

    # Select Mic
    if p_args.local:
        # Use Local text mic
        used_mic = USE_TEXT_MIC
    elif not p_args.batch_filename is None:
        # Use batched mode mic, pass a file too
        used_mic = USE_BATCH_MIC

    #parse given batch file and get the filenames or commands
    batchfilecommands = []
    for line in p_args.batch_filename:
        line = line.partition('#')[0]
        if len(line.rstrip()) > 0:
            batchfilecommands.append(line.rstrip())

    #there should be something in the file
    if len(batchfilecommands) == 0:
        parser.error("The file %s has no content" % p_args.batch_filename.name)
        p_args.batch_filename.close()
    else:
        used_mic = USE_STANDARD_MIC

    # Run Jasper
    app = application.Jasper(use_mic=used_mic,
                             batchfilecontent=batchfilecommands)
    if p_args.list_plugins:
        app.list_plugins()
        sys.exit(1)
    elif p_args.list_audio_devices:
        app.list_audio_devices()
        sys.exit(0)
    app.run()


if __name__ == '__main__':
    main()
