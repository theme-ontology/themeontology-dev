from .field import TOField
from .parser import TOParser


class TOEntry:
    cfg = None
    order = None
    
    def __init__(self, lines=None):
        self.cfg = self.cfg or {}
        self.order = self.order or []
        self.name = ""
        self.fields = []
        self.source = []
        self.parents = []
        self.children = []
        self.links = []
        if lines:
            self.populate(lines)

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.fields)
        )

    def iter_fields(self, reorder=False, skipunknown=False):
        """
        Iterate over the fields contained.
        Args:
            reorder: bool
                If True, use canonical order for fields.
            skipunknown: bool
                If True, omit deprecated and unknown fields.
        """
        lu = {f.name: f for f in self.fields}
        order = self.order if reorder else [f.name for f in self.fields]
        for fieldname in order:
            field = lu.get(fieldname, None)
            if field:
                if fieldname in self.cfg:
                    if skipunknown and self.cfg[fieldname].get("deprecated", False):
                        pass
                    else:
                        yield field

    def populate(self, lines):
        """
        Interpret a list of text lines as an "entry", assuming they conform
        to the required format.
        Args:
            lines: list of strings
        """
        self.source.extend(lines)
        cleaned = []
        for line in lines:
            cline = line.strip()
            if cline or (cleaned and cleaned[-1]):
                cleaned.append(cline)  # no more than one blank line in a row
        assert len(cleaned) > 1 and cleaned[1].startswith("==="), "missing name"
        while cleaned and not cleaned[-1]:
            cleaned.pop()
        self.name = cleaned[0]
        for fieldlines in TOParser.iter_fields(cleaned):
            while fieldlines and not fieldlines[-1]:
                fieldlines.pop()
            name = fieldlines[0].strip(": ")
            fieldconfig = self.cfg.get(name, {})
            self.fields.append(TOField(fieldlines, fieldconfig))

    def setup(self):
        """
        This should be called after the ontology has been populated, to link entries
        to each other where appropriate.
        """
        pass

    def validate(self):
        """
        Report on problems with the syntax of the entry.
        Returns:
            yields warnings as strings.
        """
        junklines = []
        for idx, line in enumerate(self.source):
            if idx > 1:
                if line.startswith("::"):
                    break
                elif line.strip():
                    junklines.append(line)
        if junklines:
            junkmsg = '/'.join(junklines)
            if len(junkmsg) > 13:
                junkmsg = junkmsg[:10] + "..."
            yield u"{}: junk in entry header: {}".format(self.name, junkmsg)
        for field in self.fields:
            if field.name not in self.cfg:
                yield u"{}: unknown field '{}'".format(self.name, field.name)

    def text_canonical(self):
        """
        Returns:
            A text blob representing this entry in its canonical format.
        """
        lines = [self.name, "=" * len(self.name), ""]
        for field in self.iter_fields(reorder=True, skipunknown=True):
            lines.append(field.text_canonical())
            lines.append("")
        return "\n".join(lines)

    def get(self, fieldname):
        """
        Returns:
        The field named fieldname, if there is one.
        """
        for field in self.fields:
            if field.name == fieldname:
                return field
        fieldconfig = self.cfg.get(fieldname, {})
        self.fields.append(TOField([], fieldconfig, name=fieldname))
        return self.fields[-1]
