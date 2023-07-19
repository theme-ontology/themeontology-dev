# Copyright 2021, themeontology.org
"""
This package shall contain all definitions required to parse data in
https://github.com/theme-ontology/theming and contain nothing that is not required for
that purpose. It shall have no external dependencies that aren't bundled with the
official Python versions supported.
"""
import codecs
from collections import defaultdict

from .impl.core import TOObject, a
from .impl.parser import TOParser

DEFAULT_URL = "https://github.com/theme-ontology/theming"


def remote(url=DEFAULT_URL):
    return TOParser.add_url(empty(), url)


def files(paths=None):
    return TOParser.add_files(empty(), paths)


def empty():
    return ThemeOntology()


class ThemeOntology(TOObject):
    theme = a({})
    story = a({})
    entries = a(defaultdict(list))

    def __str__(self):
        return f"<{len(self.theme)} themes, {len(self.story)} stories>"

    def stories(self):
        for story in self.story.values():
            yield story

    def themes(self):
        for theme in self.theme.values():
            yield theme

    def validate(self):
        yield from self.validate_entries()
        yield from self.validate_storythemes()
        yield from self.validate_cycles()

    def validate_entries(self):
        """Validate basic format of theme and story entries.
        """
        lookup = defaultdict(dict)
        for path, entries in self.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield u"{}: {}".format(path, warning)
                if entry.name in lookup[type(entry)]:
                    yield u"{}: Multiple {} with name '{}'".format(
                        path, type(entry), entry.name)

    def validate_storythemes(self):
        """Detect undefined themes used in stories.
        """
        for story in self.stories():
            for weight in ["choice", "major", "minor", "not"]:
                field = "{} Themes".format(weight.capitalize())
                for kw in story.get(field):
                    if kw.keyword not in self.theme:
                        yield u"{}: Undefined '{} theme' with name '{}'".format(
                            story.name, weight, kw.keyword)

    def validate_cycles(self):
        """Detect cycle (stops after first cycle encountered).
        """
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
