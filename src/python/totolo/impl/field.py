from .parser import TOParser
from .keyword import TOKeyword


class TOField:
    def __init__(self, lines=None, fieldconfig=None, name=''):
        self.name = name
        self.source = []
        self.data = []
        self.fieldconfig = fieldconfig or {}
        self.parts = []
        if lines:
            self.populate(lines)

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.data)
        )

    def __str__(self):
        return self.text_canonical_contents()

    def __iter__(self):
        for part in self.iter_parts():
            yield part

    def populate(self, lines):
        """
        Interpret a list of text lines as a "field", assuming they conform
        to the required format.
        Args:
            lines: list of strings
        """
        self.source.extend(lines)
        self.name = lines[0].strip(": ")
        self.data = lines[1:]
        self.parts = []
        fieldtype = self.fieldconfig.get("type", "blob")
        if fieldtype == "kwlist":
            for kwtuple in TOParser.iter_kwitems(self.data):
                self.parts.append(TOKeyword(*kwtuple))
        elif fieldtype == "list":
            for item in TOParser.iter_listitems(self.data):
                self.parts.append(item)
        elif fieldtype == "text":
            self.parts.append(lib.textformat.add_wordwrap("\n".join(self.data)).strip())
        else:
            self.parts.append('\n'.join(self.data))

    def iter_parts(self):
        """
        Iterater over components in the data of this field.
        """
        for part in self.parts:
            yield part

    def text_canonical_contents(self):
        """
        Returns:
            A text blob representing the contents of this field in its canonical format.
        """
        parts = [str(x) for x in self.iter_parts()]
        return u'\n'.join(parts)

    def text_canonical(self):
        """
        Returns:
            A text blob representing this field in its canonical format.
        """
        parts = [u":: {}".format(self.name)]
        parts.extend(str(x) for x in self.iter_parts())
        return u'\n'.join(parts)

    def delete(self, kw):
        """
        Delete a keyword.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        todelete = set()
        if fieldtype == "kwlist":
            for idx, part in enumerate(self.parts):
                if part.keyword == kw:
                    todelete.add(idx)
        self.parts = [p for idx, p in enumerate(self.parts) if idx not in todelete]
        return min(todelete) if todelete else len(self.parts)

    def update(self, kw, keyword=None, motivation=None, capacity=None, notes=None):
        """
        Update keyword data.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        if fieldtype == "kwlist":
            for part in self.parts:
                if part.keyword == kw:
                    if keyword is not None:
                        part.keyword = keyword
                    if motivation is not None:
                        part.motivation = motivation
                    if capacity is not None:
                        part.capacity = capacity
                    if notes is not None:
                        part.notes = notes

    def insert(self, idx=None, keyword="", motivation="", capacity="", notes=""):
        """
        Insert a new keyword at location idx in the list.
        If idx is None, append.
        """
        if idx is None:
            idx = len(self.parts)
        self.parts.insert(idx, TOKeyword(keyword, capacity=capacity, motivation=motivation, notes=notes))
