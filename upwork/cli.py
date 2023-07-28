import argparse
from dataclasses import dataclass

_SELENIUM_DEFAULT_SERVER_ADDR = 'http://127.0.0.1:4444'
_SELENIUM_DEFAULT_WAIT_TIMEOUT = 60

_SCAN_DEFAULT_OUT_FILENAME = 'scan.json'


@dataclass(frozen=True)
class Args:
    user: str
    password: str
    secret_answer: str

    out_file: str

    selenium_server_url: str
    selenium_wait_timeout: float


def _add_credential_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('-u', '--user',
                        dest='user',
                        metavar='string',
                        required=True)
    parser.add_argument('-p', '--password',
                        dest='password',
                        metavar='string',
                        required=True)
    parser.add_argument('-s', '--secret-answer',
                        dest='secret_answer',
                        metavar='string',
                        required=True)


def _add_selenium_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group('Selenium Options')
    group.add_argument('--selenium-server-url',
                       dest='selenium_server_url',
                       default=_SELENIUM_DEFAULT_SERVER_ADDR,
                       metavar='string')
    group.add_argument('--selenium-wait-timeout',
                       dest='selenium_wait_timeout',
                       default=_SELENIUM_DEFAULT_WAIT_TIMEOUT,
                       type=float,
                       metavar='float')


def _add_scan_result_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group('Output Options')
    group.add_argument('-o', '--out-file',
                       dest='out_file',
                       default=_SCAN_DEFAULT_OUT_FILENAME,
                       metavar='string', )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='upwork',
                                     usage='upwork [options] <args>')

    _add_credential_args(parser)
    _add_selenium_args(parser)
    _add_scan_result_args(parser)

    return parser


def parse_args(argv: list[str]) -> Args:
    parser = _build_parser()
    args = parser.parse_args(argv)

    return Args(user=args.user,
                password=args.password,
                secret_answer=args.secret_answer,

                out_file=args.out_file,

                selenium_server_url=args.selenium_server_url,
                selenium_wait_timeout=args.selenium_wait_timeout)
