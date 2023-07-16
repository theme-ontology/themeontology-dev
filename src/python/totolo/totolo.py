# Copyright 2021, themeontology.org
"""
This module shall contain all definitions required to parse data in
https://github.com/theme-ontology/theming and contain nothing that is not required for 
that purpose. It shall have no external dependencies that aren't bundled with the
official Python versions supported.
"""
import codecs
import os.path
from collections import defaultdict

import totolo.lib.files
import totolo.lib.git
import totolo.lib.textformat
from totolo.impl import TOParser, TOStory, TOTheme

DEFAULT_URL = "https://github.com/theme-ontology/theming"


def fetch(url=DEFAULT_URL):
    if any(url.endswith(x) for x in [".tar", ".tar.gz"]):
        with totolo.lib.files.remote_tar(url) as dirname:
            to = read(dirname, imply_collection=True)
    else:
        with totolo.lib.git.remote_headversion(url) as dirname:
            to = read(dirname, imply_collection=True)
    return to


def read(paths=None, imply_collection=False):
    return ThemeOntology(paths, imply_collection=imply_collection)


def empty():
    return ThemeOntology()




class ThemeOntology(object):
    def __init__(self, paths=None, imply_collection=False):
        self.theme = {}
        self.story = {}
        self.entries = defaultdict(list)
        self._imply_collection = imply_collection
        if paths:
            if isinstance(paths, (list, tuple)):
                for path in paths:
                    self.read(path)
            else:
                self.read(paths)

    def stories(self):
        """
        Iterate over all story entries defined in no particular order.
        """
        for story in self.story.values():
            yield story

    def themes(self):
        """
        Iterate over all theme entries defined in no particular order.
        """
        for theme in self.theme.values():
            yield theme

    def read(self, path):
        """
        Reads a file if path is a file name, or all files underneath a
        directory if path is a directory name.
        Args:
            path: a file or directory path
        """
        if os.path.isdir(path):
            for filepath in totolo.lib.files.walk(path, r".*\.(st|th)\.txt$"):
                self.read(filepath)
        else:
            with codecs.open(path, "r", encoding='utf-8') as fh:
                if path.endswith(".th.txt"):
                    self.read_themes(fh, path)
                elif path.endswith(".st.txt"):
                    self.read_stories(fh, path)
                else:
                    raise ValueError(
                        "Path must end with .th.txt ot .st.txt to indicate whether it" 
                        "contains themes or stories.")

    def read_stories(self, lines, path="<api>"):
        """
        Read story entries from text or iterable of lines of text.
        """
        collection_entry = None
        if isinstance(lines, str):
            lines = lines.splitlines()
        for idx, entrylines in enumerate(TOParser.iter_entries(lines)):
            entry = TOStory(entrylines)
            entry.ontology = self
            self.entries[path].append(entry)
            self.story[entry.name] = entry
            if idx == 0:
                mycols = entry.get("Collections").parts
                if mycols and mycols[0] == entry.sid:
                    collection_entry = entry
            if idx > 0 and self._imply_collection and collection_entry:
                field = collection_entry.get("Component Stories")
                field.parts.append(entry.sid)

    def read_themes(self, lines, path="<api>"):
        """
        Read theme entries from text or iterable of lines of text.
        """
        if isinstance(lines, str):
            lines = lines.splitlines()
        for idx, entrylines in enumerate(TOParser.iter_entries(lines)):
            entry = TOTheme(entrylines)
            entry.ontology = self
            self.entries[path].append(entry)
            self.theme[entry.name] = entry

    def validate(self):
        """
        Yields warnings about recognized problems with the data.
        """
        # validate format of theme and story entries
        lookup = defaultdict(dict)
        for path, entries in self.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield u"{}: {}".format(path, warning)
                if entry.name in lookup[type(entry)]:
                    yield u"{}: Multiple {} with name '{}'".format(
                        path, type(entry), entry.name)

        # detect undefined themes used in stories
        for story in self.stories():
            for weight in ["choice", "major", "minor", "not"]:
                field = "{} Themes".format(weight.capitalize())
                for kw in story.get(field):
                    if kw.keyword not in self.theme:
                        yield u"{}: Undefined '{} theme' with name '{}'".format(
                            story.name, weight, kw.keyword)

        # detect cycle (stops after first cycle encountered)
        parents = {}
        for theme in self.themes():
            parents[theme.name] = [parent for parent in theme.get("Parents")]

        def dfs(current, tpath=None):
            tpath = tpath or []
            if current in tpath:
                return u"Cycle: {}".format(tpath[tpath.index(current):])
            else:
                tpath.append(current)
                for parent in parents[current]:
                    msg = dfs(parent, tpath)
                    if msg:
                        return msg
                tpath.pop()
            return None

        for theme in self.themes():
            msg = dfs(theme.name)
            if msg:
                yield msg
                break

    def write_clean(self, verbose=False):
        """
        Write the ontology back to its source file while cleaning up syntax and
        omitting unknown field names.
        """
        for path, entries in self.entries.items():
            lines = []
            for entry in entries:
                lines.append(entry.text_canonical())
                lines.append("")
            with codecs.open(path, "w", encoding='utf-8') as fh:
                if verbose:
                    print(path)
                fh.writelines(x + "\n" for x in lines)

    def print_warnings(self):
        """
        Run validate and print warnings to stdout.
        """
        for msg in self.validate():
            print(msg)

