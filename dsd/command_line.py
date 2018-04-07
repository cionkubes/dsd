#!/usr/bin/env python

import sys
import collections
import os
import tempfile
import yaml


def elem_merge(x):
    if isinstance(x, dict):
        return {key: elem_merge(val) for key, val in x.items()}
    elif isinstance(x, list):
        return [elem_merge(val) for val in x]
    elif isinstance(x, str):
        return x.format(**os.environ)
    else:
        return x


def merge(a, b):
    if isinstance(a, dict) and isinstance(b, collections.Mapping):
        return dict_merge(a, b)
    elif isinstance(a, list) and isinstance(b, collections.Sequence):
        return list_merge(a, b)
    else:
        return elem_merge(b)


def dict_merge(into, dict):
    result = {}
    result.update(into)

    for key in dict.keys():
        result[key] = merge(into[key] if key in into else {}, dict[key])

    return result


def list_merge(into, list):
    print("list")
    result = []
    result.extend(into)
    result.extend(list)

    return [elem_merge(x) for x in result]


def main():
    filename = sys.argv[1]

    if sys.argv[2] in ('--out', '-o'):
        docker = False
        del sys.argv[2]
    else:
        docker = True

    try:
        param_sep = sys.argv.index('--')
    except:
        param_sep = -1

    profiles = sys.argv[2:param_sep]
    args = sys.argv[param_sep+1:]

    with open(filename) as fp:
        document = {}

        docs = yaml.load_all(fp)
        document = merge(document, next(docs))

        for doc in docs:
            if doc['profile'] in profiles:
                del doc['profile']
                document = merge(document, doc)

    if docker:
        with tempfile.NamedTemporaryFile(delete=False) as fd:
            path = fd.name
            fd.write(yaml.dump(document, encoding='utf-8'))

        cmd = "docker stack deploy -c {} {}".format(path, " ".join(args))
        print(cmd)
        os.system(cmd)
        os.remove(path)
    else:
        yaml.safe_dump(document, sys.stdout, allow_unicode=True,
                       default_flow_style=False)
