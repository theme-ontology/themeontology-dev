
class TOKeyword:
    def __init__(self, keyword, capacity=None, motivation=None, notes=None):
        self.keyword = keyword
        self.motivation = motivation
        self.capacity = capacity
        self.notes = notes
        assert(len(keyword.strip()) > 0)

    def __str__(self):
        pm = u" [{}]".format(self.motivation) if self.motivation else ""
        pc = u" <{}>".format(self.capacity) if self.capacity else ""
        pn = u" {{{}}}".format(self.notes) if self.notes else ""
        return u"{}{}{}{}".format(self.keyword, pc, pm, pn)

    def __repr__(self):
        return 'TOKeyword<{}>'.format(str(self))

