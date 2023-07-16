# Copyright 2023, themeontology.org
import contextlib

import totolo.lib.files


@contextlib.contextmanager
def remote_headversion(github_url: str):
    parts = [github_url, "archive/refs/heads/master.tar.gz"]
    url = '/'.join(x.strip('/') for x in parts)
    with totolo.lib.files.remote_tar(url) as dirname:
        yield dirname
