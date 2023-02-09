import argparse
import enum
import os
from typing import Optional, TextIO

from requests import Response, post

from pb import recover_key

_API_URI = 'https://pastebin.com/api/api_post.php'


def paste_file(
    file: TextIO, /,
    name: Optional[str] = None,
    description: Optional[str] = None,
    format: Optional[str] = None,
    *args, **kwargs
):
    """Pastes a file to pastebin.com"""
    name = name or os.path.basename(file.name)
    format = format or _format_from_extension(
        os.path.splitext(file.name)[1][1:])

    return paste(file.read(), name, description, format, *args, **kwargs)


def handle_response(response: Response):
    print(response.text)


class Visibility(enum.IntEnum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2


def drop_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


_extension_formats = {
    'ada': 'ada',
    'arm': 'arm',
    'asm': 'asm',
    'asp': 'asp',
    'bash': 'bash',
    'bat': 'dos',
    'bibtex': 'bibtex',
    'c': 'c',
    'cs': 'csharp',
    'cc': 'cpp',
    'cpp': 'cpp',
    'c++': 'cpp',
    'clj': 'clojure',
    'cmake': 'cmake',
    'css': 'css',
    'd': 'd',
    'dart': 'dart',
    'html': 'html5',
    'java': 'java',
    'js': 'javascript',
    'json': 'json',
    'latex': 'latex',
    'lua': 'lua',
    'm': 'matlab',
    'md': 'markdown',
    'py': 'python',
}


def _format_from_extension(ext: str) -> Optional[str]:
    return _extension_formats.get(ext, None)


def paste(
    data: str, /,
    name: Optional[str] = None,
    description: Optional[str] = None,
    format: Optional[str] = None,
    dev_key: Optional[str] = None,
    user_key: Optional[str] = None,
    visibility: Visibility = Visibility.PRIVATE,
    expire_date: Optional[str] = None,
):
    """Pastes data to pastebin.com"""
    dev_key = dev_key or recover_key()
    if not dev_key:
        raise ValueError(
            'Could not recover API key. Provide one or set the environment variable PASTEBIN_API_KEY.')

    data = data.encode('utf-8')
    form = {
        'api_dev_key': dev_key,
        'api_user_key': user_key,
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


_expire_date = ['N', '10M', '1H', '1D', '1W', '2W', '1M', '6M', '1Y']


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    parser.add_argument('--name', '-n')
    parser.add_argument('--description', '-d')
    parser.add_argument('--format', '-f')
    parser.add_argument('--dev-key', '-k')
    parser.add_argument('--visibility', '-v',
                        choices=['public', 'unlisted', 'private'],
                        default='public'
                        )
    parser.add_argument('--expire-date', '-e', choices=_expire_date)

    user_grp = parser.add_mutually_exclusive_group()
    user_grp.add_argument('--user-key', '-u')
    user_grp.add_argument('--user-key-file', '-U', type=argparse.FileType('r'))

    return parser


def main():
    args = argparser().parse_args()
    visibility = args.visibility and Visibility[args.visibility.upper()]
    user_key = args.user_key or args.user_key_file and args.user_key_file.read()
    paste_file(
        args.file,
        name=args.name,
        description=args.description,
        format=args.format,
        dev_key=args.dev_key,
        user_key=user_key,
        visibility=visibility,
        expire_date=args.expire_date,
    )


if __name__ == '__main__':
    main()
