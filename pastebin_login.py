import argparse
from typing import Optional
from getpass import getpass
from requests import Response, post

from pb import recover_key

_API_URI = 'https://pastebin.com/api/api_login.php'


def prompt_password() -> str:
    """Prompts the user for a password"""
    return getpass('Password: ')


def handle_response(response: Response):
    print(response.text.encode('utf-8'))


def login(user: str, password: str, key: Optional[str] = None):
    """Logs in to pastebin.com"""
    key = key or recover_key()
    if not key:
        raise ValueError('No API key found')

    response = post(
        _API_URI,
        data={
            'api_dev_key': key,
            'api_user_name': user,
            'api_user_password': password,
        }
    )

    handle_response(response)


def argument_parser() -> argparse.ArgumentParser:
    """Returns an argument parser for the script"""
    parser = argparse.ArgumentParser(
        description='Logs in to pastebin.com')
    parser.add_argument(
        'user',
        help='The user to log in as')
    parser.add_argument(
        '-p', '--password',
        help='The password to log in with')
    parser.add_argument(
        '-k', '--key',
        help='The API key to use')
    return parser


def main():
    """The main entry point of the script"""
    parser = argument_parser()
    args = parser.parse_args()

    login(args.user, args.password or prompt_password(), args.key)


if __name__ == '__main__':
    main()
