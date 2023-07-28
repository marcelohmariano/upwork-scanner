import sys

from upwork import browser
from upwork import cli
from upwork import scan

args = cli.parse_args(sys.argv[1:])

credentials = scan.Credentials(username=args.user,
                               password=args.password,
                               secret_answer=args.secret_answer)

driver = browser.Driver(selenium_server_url=args.selenium_server_url,
                        selenium_wait_timeout=args.selenium_wait_timeout)

with driver:
    res = scan.run(driver, credentials)
    res.save(args.out_file)
