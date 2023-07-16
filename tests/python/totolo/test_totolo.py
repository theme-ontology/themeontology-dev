# Copyright 2021, themeontology.org
import os.path
import sys
from pathlib import Path

import lib.log
import totolo


class TestFunctionality:
    def test_to(self):
        """
        Test on data snapped from the ontology.
        """
        to = totolo.fetch()
        print(to)

    def test_cycle_warning(self):
        """
        Ensure we get warnings about theme cycles.
        """
        to = totolo.read("data/tests/cycles1.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1
        to = totolo.read("data/tests/cycles2.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1
        to = totolo.read("data/tests/cycles3.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1

