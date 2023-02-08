import os
from os import PathLike
from typing import Optional, TextIO
import argparse
import enum
from requests import post, Response

Path = str | bytes | os.PathLike

_API_URI = 'https://pastebin.com/api/api_post.php'


def paste_file(file: TextIO, name: Optional[str] = None, *args, **kwargs):
    """Pastes a file to pastebin.com"""
    name = name or os.path.basename(file.name)
    return paste(file.read(), name, *args, **kwargs)


def recover_key() -> Optional[str]:
    """Returns the API key from the environment variable PASTEBIN_API_KEY"""
    return os.environ.get('PASTEBIN_API_KEY', None)


def handle_response(response: Response):
    print(response.text)


class Visibility(enum.IntEnum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2


def paste(
    data: str, /,
    name: Optional[str] = None,
    description: Optional[str] = None,
    format: Optional[str] = None,
    dev_key: Optional[str] = None,
    visibility: Visibility = Visibility.PRIVATE,
    expire_date: Optional[str] = None,

):
    """Pastes data to pastebin.com"""
    dev_key = dev_key or recover_key()

    data = data.encode('utf-8')
    form = {
        'api_dev_key': dev_key,
        'api_paste_code': data,
        'api_option': 'paste',
        'api_paste_name': name,
        'api_paste_description': description,
        'api_paste_format': format,
        'api_paste_private': visibility.value,
        'api_paste_expire_date': expire_date,

    }
    form = {k: v for k, v in form.items() if v is not None}

    response = post(_API_URI, data=form)
    handle_response(response)


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    parser.add_argument('--name', '-n')
    parser.add_argument('--description', '-d')
    parser.add_argument('--format', '-f')
    parser.add_argument('--dev-key', '-k')
    parser.add_argument('--visibility', '-v', type=str,
                        choices=['public', 'unlisted', 'private'], default='public')
    parser.add_argument('--expire-date', '-e')
    return parser


def main():
    args = argparser().parse_args()
    visibility = args.visibility and Visibility[args.visibility.upper()]
    paste_file(args.file, args.name, args.description, args.format,
               args.dev_key, visibility, args.expire_date)


if __name__ == '__main__':
    main()
