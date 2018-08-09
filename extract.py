#!/usr/bin/env python3
import logger; logger.setup('botwtools')
log = logger.logging.getLogger()
import sys
import codec


def print_usage():
    print(("Usage:\n"
        "  {name} --list file\n"
        "  {name} --extract file destination").format(
            name=sys.argv[0]))
    print("Available encoders:", ', '.join(map(
        lambda f: f.decode('utf-8'),
        sorted(codec.encoders.keys())
    )))
    print("Available decoders:", ', '.join(map(
        lambda f: f.decode('utf-8'),
        sorted(codec.decoders.keys())
    )))
    sys.exit(1)


def main(*args):
    if len(args) < 2:
        print_usage()

    path = args[1]
    with open(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        if args[0] == '--list': dest = None
        else: dest = args[2]
        decoder = decoder(file, dest)

        if args[0] == '--list': decoder.printList()
        elif args[0] == '--extract': decoder.unpack()
        else: print_usage()

        # XXX recursive extraction: try to extract each extracted file,
        # until we find one we don't support.


if __name__ == '__main__':
    try:
        main(*sys.argv[1:])
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
