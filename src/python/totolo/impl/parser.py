import re
from typing import Iterable, Generator, List, Tuple


class TOParser:
    @classmethod
    def iter_entries(cls, lines: Iterable[str]) -> Generator[str, None, None]:
        """
        Iterate through the "entries" in a text file. An entry is a block of lines
        that starts with a title line, followed by a line starting with "===".
        """
        linebuffer = []
        for line in lines:
            line = line.rstrip()
            if line.startswith("===") and linebuffer:
                prevlines = linebuffer[:-1]
                if any(x for x in prevlines):
                    yield prevlines
                linebuffer = [linebuffer[-1]]
            linebuffer.append(line)
        if linebuffer and any(line for line in linebuffer):
            yield linebuffer

    @classmethod
    def iter_fields(cls, lines: Iterable[str]) -> List[str]:
        """
        Iterate through the fields of an entry. Fields are blocks starting with ::
        """
        linebuffer = []
        for line in lines:
            if line.startswith("::"):
                if linebuffer:
                    yield linebuffer
                linebuffer = [line]
            elif linebuffer:
                linebuffer.append(line)
        if linebuffer:
            yield linebuffer

    @classmethod
    def iter_listitems(cls, lines: Iterable[str]) -> str:
        """
        Turn a list of strings into items. Items may be newline or comma separated.
        """
        for line in lines:
            # note: once upon a time we used to have multiple items separated by commas 
            # on a single line but that is no longer permitted.
            item = line.strip()
            if item:
                yield item

    @classmethod
    def iter_kwitems(
        cls, lines: Iterable[str]
    ) -> Generator[Tuple[str, str, str, str], None, None]:
        """
        Turn a list of strings into kewyword items. Items may be newline or comma 
        separated. Items may contain data in () [] {} parentheses.
        """

        def dict2row(tokendict):
            tkw = tokendict.get("", "").strip()
            tmotivation = tokendict.get("[", "").strip()
            tcapacity = tokendict.get("<", "").strip()
            tnotes = tokendict.get("{", "").strip()
            return tkw, tcapacity, tmotivation, tnotes

        field = "\n".join(lines)
        token = {}
        delcorr = {"[": "]", "{": "}", "<": ">"}
        farr = re.split("([\[\]\{\}\<\>,\\n])", field)
        state = ""
        splitters = ",\n"

        for part in farr:
            if part in delcorr:
                state = part
            elif part in delcorr.values():
                if delcorr.get(state, None) == part:
                    state = ""
                else:
                    raise AssertionError(
                        "Malformed field (bracket mismatch):\n  %s" % field
                    )
            elif part in splitters and not state:
                tokrow = dict2row(token)
                if not tokrow[0].strip():
                    pass  # we allow splitting by both newline and comma
                else:
                    yield tokrow
                token = {}
            else:
                token[state] = token.get(state, "") + part

        tokrow = dict2row(token)
        if tokrow[0].strip():
            yield dict2row(token)
