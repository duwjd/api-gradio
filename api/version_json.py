#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import argparse

"""
    version value could be digit with alpha char, i.e. 51p1
    version value data type could be int, str
    i.e.
        {major=51, minor=0, patch=0, build=0, identifier=''}
        {major='51p1', minor=0, patch=0, build=0, identifier=''}
"""

_VERSION_MODULE = "1.0"


def get_version_str_from_ver(ver, format="whl_filename"):
    """
    get version string from version dict.
    :param ver: dict, version dict
    :return:
        version string
    """
    ver_str = ""
    ver_str += (str(ver["major"]) if "major" in ver else "0") + "."
    ver_str += (str(ver["minor"]) if "minor" in ver else "0") + "."
    ver_str += (str(ver["patch"]) if "patch" in ver else "0") + "."
    ver_str += str(ver["build"]) if "build" in ver else "0"
    if ("identifier" in ver) and (len(ver["identifier"]) > 0):
        if format == "whl_filename":
            whl_id = (ver["identifier"]).lower()
            if whl_id.startswith("alpha"):
                whl_id = whl_id.replace("alpha", "a")
            elif whl_id.startswith("beta"):
                whl_id = whl_id.replace("beta", "b")
            elif whl_id.startswith("rc"):
                whl_id = whl_id.replace("rc", "rc")
            else:
                # invalid version identifier in whl_filename
                whl_id = ""

            if len(whl_id) > 1 and (whl_id[-1].isdigit() is False):
                whl_id += "0"

            ver_str += whl_id
        else:
            ver_str += " (" + str(ver["identifier"]) + ")"

    return ver_str


def get_version_str(filename, format="whl_filename"):
    """
    get version string from version.json file
    :param filename: string, file path of version.json
    :return:
        success, version string
        fail, None
    """
    ret = None
    with open(filename) as f:
        data = json.load(f)
        if "version" in data:
            ret = get_version_str_from_ver(data["version"], format=format)
    return ret


def get_version_from_str(ver_str):
    """
    get version dict from version string
    :param ver_str: string, version string
    :return:
        success, dict, version
        fail, None
    """
    ret = None

    def get_version_value(val):
        if val.isnumeric():
            return int(val)
        return val

    if isinstance(ver_str, str):
        ver_tokens = re.split(r"[.-]+", ver_str.strip())
        len_ver_tokens = len(ver_tokens)
        if len_ver_tokens > 0:
            ver_major = 0
            ver_minor = 0
            ver_patch = 0
            ver_build = 0
            ver_identifier = ""

            try:
                ver_major = get_version_value(ver_tokens[0])
                ver_identifier = ""
                if len_ver_tokens > 1:
                    ver_minor = get_version_value(ver_tokens[1])
                    if len_ver_tokens > 2:
                        ver_patch = get_version_value(ver_tokens[2])
                        if len_ver_tokens > 3:
                            ver_build = get_version_value(ver_tokens[3])
                            if len_ver_tokens > 4:
                                ver_identifier = str(ver_tokens[4])

            except ValueError:
                pass

            ret = {
                "major": ver_major,
                "minor": ver_minor,
                "patch": ver_patch,
                "build": ver_build,
                "identifier": ver_identifier,
            }

    return ret


def cmp_version_value(lval, rval):
    # version value could be digit with alpha char, i.e. 51p1
    def parse_version_value(val):
        ret = []
        item = ""
        check_digit = True
        for ch in val:
            if ch.isdigit():
                if check_digit is False:
                    ret.append(item)
                    item = ""
                    check_digit = True
                item += ch
            elif ch.isalpha():
                if check_digit is True:
                    ret.append(item)
                    item = ""
                    check_digit = False
                item += ch
            else:
                # invalid char, ignore it
                pass

        ret.append(item)

        return ret

    lvals = parse_version_value(lval)
    rvals = parse_version_value(rval)

    ret = 0
    i = 0
    while True:
        if i >= len(lvals) or i >= len(rvals):
            ret = len(lvals) - len(rvals)
            break
        elif lvals[i] == rvals[i]:
            pass
        elif lvals[i].isnumeric() and rvals[i].isnumeric():
            ret = int(lvals[i]) - int(rvals[i])
            if ret != 0:
                break
        elif lvals[i] > rvals[i]:
            ret = 1
            break
        else:  # lvals[i] < rvals[i]:
            ret = -1
            break

        i += 1

    return ret


def cmp_version(lver, rver):
    """
    compare, right version and left version

    :param lver: dict, left version
    :param rver: dict, right version
    :return:
        == 0, lver == rver,
        > 0, lver > rver,
        < 0, lver < rver,
        ValueError: invalid value
    """
    ret = cmp_version_value(str(lver.get("major")), str(rver.get("major")))
    if ret == 0:
        ret = cmp_version_value(
            str(lver.get("minor", "0")), str(rver.get("minor", "0"))
        )
        if ret == 0:
            ret = cmp_version_value(
                str(lver.get("patch", "0")), str(rver.get("patch", "0"))
            )
            if ret == 0:
                ret = cmp_version_value(
                    str(lver.get("build", "0")), str(rver.get("build", "0"))
                )
                if ret == 0:
                    ret = cmp_version_value(
                        str(lver.get("identifier", "")), str(rver.get("identifier", ""))
                    )

    return ret


def parser_is_valid_file(parser, arg):
    if os.path.exists(arg) is False:
        parser.error("The file was not exist, {}".format(arg))
    else:
        return arg


def main():
    help_desc = "print version string, ver.({})".format(_VERSION_MODULE)
    help_desc += " (C)10k1m.com, Inc. All Rights Reserved."

    parser = argparse.ArgumentParser(description=help_desc)
    parser.add_argument(
        "VERSION_JSON_FILE",
        nargs="?",
        help="version json file",
        default="./version.json",
        type=lambda x: parser_is_valid_file(parser, x),
    )
    args = parser.parse_args()

    ver_str = get_version_str(args.VERSION_JSON_FILE, format="whl_filename")
    if ver_str is None:
        print("0.0.0.0")
        return 1

    print(ver_str)
    return 0


if __name__ == "__main__":
    exit(main())
