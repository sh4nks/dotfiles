#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    pwcomp
    ~~~~~~

    pwcomp is a simple command line utility to compare the password dumps
    from chrome, firefox and bitwarden.

    It's primary focus is to compare the chrome password dump with
    bitwardens' in order to get completely rid of Google Chrome and
    will return all entries which are not in bitwarden.

    The url validator has been taken from the 'validators' project:
    https://github.com/kvesteri/validators
    and is licensed under the MIT License.

    :copyright: (c) 2021 by Peter Justin.
    :license: GPLv3, see LICENSE for more details.
"""
import os
import sys
import argparse
import re
import csv
import urllib.parse
import textwrap

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("'rich' is required for pwcomp.py to work.")
    print(
        "You can install rich with 'pip install rich' or with your "
        "distirbutions package manager!"
    )
    sys.exit(1)

# taken from validators.url
ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"

regex = re.compile(  # noqa: W605
    r"^"
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
    # user:pass authentication
    r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + ip_middle_octet + r"{2}" + ip_last_octet + r")|"
    r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + r")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + r"))"
    r"|"
    # private & local hosts
    r"(?P<private_host>" r"(?:localhost))" r"|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + ip_middle_octet + r"{2}"
    r"" + ip_last_octet + r")"
    r"|"
    # IPv6 RegEx from https://stackoverflow.com/a/17871737
    r"\[("
    # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
    # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,7}:|"
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])" r")\]|"
    # host name
    r"(?:(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)"
    # domain name
    r"(?:\.(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:(?:xn--[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]{2,})|"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff]{2,}))"
    r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:/[-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    r"(?:\?\S*)?"
    # fragment
    r"(?:#\S*)?" r"$",
    re.UNICODE | re.IGNORECASE,
)

pattern = re.compile(regex)


def valid_url(value, public=False):
    """
    Return whether or not given value is a valid URL.
    If the value is valid URL this function returns ``True``, otherwise
    :class:`~validators.utils.ValidationFailure`.
    This validator is based on the wonderful `URL validator of dperini`_.

    Taken from validators.url.

    :param value: URL address string to validate
    :param public: (default=False) Set True to only allow a public IP address
    """
    result = pattern.match(value)
    if not public:
        return result

    return result and not any(
        (result.groupdict().get(key) for key in ("private_ip", "private_host"))
    )


# bitwarden: name, login_uri, login_username, login_password
# firefox: url, username, password
# google: name, url, username, password
MAPPING = {
    "google": {
        "name": "name",
        "url": "url",
        "username": "username",
        "password": "password",
    },
    "bitwarden": {
        "name": "name",
        "url": "login_uri",
        "username": "login_username",
        "password": "login_password",
    },
    "firefox": {
        "name": "url",
        "url": "url",
        "username": "username",
        "password": "password",
    },
}


def url_parser(unparsed_url):
    urls = []
    if unparsed_url.startswith(("android://", "androidapp://")):
        return None

    if unparsed_url == "":
        return None

    if not unparsed_url.startswith(("http://", "https://")):
        if "@" in unparsed_url:
            return None

        unparsed_url = "https://" + unparsed_url

    if not valid_url(unparsed_url):
        if "," in unparsed_url:
            for uri in unparsed_url.split(","):
                url = url_parser(uri)
                if url is not None:
                    urls.extend(url)
    else:
        url = urllib.parse.urlparse(unparsed_url).netloc
        urls.append(url)

    return urls


def normalize_dict(d, typ):
    m = MAPPING[typ]

    userpass_d = {}
    for item in d:
        unparsed_url = item[m["url"]] or item[m["name"]]
        urls = url_parser(unparsed_url)
        # non valid urls are None
        if urls is None:
            continue

        # print(f"{unparsed_url} = {urls}")
        username = item[m["username"]]
        password = item[m["password"]]

        name = urls[0] if urls else item[m["name"]]
        userpass_d.setdefault(name, {})
        userpass_d[name]["username"] = username
        userpass_d[name]["password"] = password
        userpass_d[name]["urls"] = urls

    return userpass_d


def read_csv_file(filename):
    d = []
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
        for kv_row in reader:
            d.append(kv_row)
    return d


def check_credentials(left_dict, right_dict, provider_left, provider_right):
    mismatch = {}
    unknown = {}
    for k_left, v_left in left_dict.items():
        found_inner = False
        for k_right, v_right in right_dict.items():
            if any(url in v_left["urls"] for url in v_right["urls"]):

                u_l = v_left["username"]
                u_r = v_right["username"]
                p_l = v_left["password"]
                p_r = v_right["password"]

                found_inner = True
                if u_l == u_r and p_l == p_r:
                    # credentials match
                    continue
                else:
                    # credentials mismatch
                    mismatch[k_right] = {
                        provider_left: (u_l, p_l),
                        provider_right: (u_r, p_r),
                    }

        if not found_inner:
            unknown[k_left] = {
                provider_left: (v_left["username"], v_left["password"]),
                provider_right: ("", ""),
            }
    return mismatch, unknown


def print_unknown(unknown, provider_left, provider_right):
    table = Table(title="Unknown Credentials")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column(f"User - {provider_left}", style="white", max_width=40)
    table.add_column(f"Password - {provider_left}", style="green", max_width=40)

    for url, userpass in unknown.items():
        table.add_row(
            url,
            userpass[provider_left][0],
            userpass[provider_left][1],
        )

    console = Console()
    console.print(table)


def print_mismatched(mismatched, provider_left, provider_right):
    table = Table(title="Mismatched Credentials")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column(f"User - {provider_left}", style="white", max_width=40)
    table.add_column(f"User - {provider_right}", style="white", max_width=40)
    table.add_column(f"Password - {provider_left}", style="green", max_width=40)
    table.add_column(
        f"Password - {provider_right}", style="green", max_width=40
    )

    for url, userpass in mismatched.items():
        table.add_row(
            url,
            userpass[provider_left][0],
            userpass[provider_right][0],
            userpass[provider_left][1],
            userpass[provider_right][1],
        )

    console = Console()
    console.print(table)


def main(
    provider_left: str, provider_right: str, input_left: str, input_right: str
):
    left_file = read_csv_file(input_left)
    right_file = read_csv_file(input_right)

    left_d = normalize_dict(left_file, provider_left)
    right_d = normalize_dict(right_file, provider_right)

    mismatched, unknown = check_credentials(
        left_d, right_d, provider_left, provider_right
    )
    print_mismatched(mismatched, provider_left, provider_right)
    print_unknown(unknown, provider_left, provider_right)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Compares two password dumps against each other.\n\n"
            "For example: \n"
            "    pwcomp.py -l ./firefox.csv -lp firefox -r ./bitwarden.csv -rp bitwarden"
            "\n"
        )
    )

    parser.add_argument(
        "-l",
        "--left",
        help=("The left dump."),
        default="firefox.csv",
    )
    parser.add_argument(
        "-lp",
        "--left-provider",
        help=(
            "The left password provider type. Either 'google', 'bitwarden' or 'firefox'"
        ),
        required=True,
    )

    parser.add_argument(
        "-r",
        "--right",
        help=(
            "The right dump. This is the base which will be compared against. This is usually bitwarden's dump."
        ),
        required=True,
    )
    parser.add_argument(
        "-rp",
        "--right-provider",
        help=(
            "The right password provider type. Either 'google', 'bitwarden' or 'firefox'"
        ),
        required=True,
    )
    results = parser.parse_args()

    if not os.path.exists(results.left):
        parser.print_help(sys.stderr)
        parser.exit(
            2,
            (
                f"Path '{results.left}' for the left dump does not exist."
                " Please enter a valid path/file.\n"
            ),
        )

    if not os.path.exists(results.right):
        parser.print_help(sys.stderr)
        parser.exit(
            2,
            (
                f"Path '{results.right}' for the right dump does not exist."
                " Please enter a valid path/file.\n"
            ),
        )

    main(
        provider_left=results.left_provider,
        provider_right=results.right_provider,
        input_left=results.left,
        input_right=results.right,
    )
