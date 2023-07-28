from upwork import cli


def test_parse_args():
    args = cli.parse_args([
        '--user', 'test@test.com',
        '--pass', 'test-pass',
        '--secret-answer', 'test-answer',
        '--selenium-server-url', 'http://test:4444',
        '--selenium-wait-timeout', '5.5'
    ])

    assert args.user == 'test@test.com'
    assert args.password == 'test-pass'
    assert args.secret_answer == 'test-answer'
    assert args.selenium_server_url == 'http://test:4444'
    assert args.selenium_wait_timeout == 5.5
