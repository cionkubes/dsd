#!/usr/bin/env python

import sys
import collections
import os
import tempfile
import yaml


def environ_constructor(loader, node):
    return node.value.format(**os.environ)


yaml.add_constructor(u'tag:yaml.org,2002:str', environ_constructor)


# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def main():
    filename = sys.argv[1]

    try:
        param_sep = sys.argv.index('--')
    except:
        param_sep = -1

    profiles = sys.argv[2:param_sep]
    args = sys.argv[param_sep+1:]

    with open(filename) as fp:
        document = {}

        docs = yaml.load_all(fp)
        dict_merge(document, next(docs))

        for doc in docs:
            if doc['profile'] in profiles:
                del doc['profile']
                dict_merge(document, doc)

    with tempfile.NamedTemporaryFile(delete=False) as fd:
        path = fd.name
        fd.write(yaml.dump(document, encoding='utf-8'))

    cmd = "docker stack deploy -c {} {}".format(path, " ".join(args))
    print(cmd)
    os.system(cmd)
    os.remove(path)
