# Copyright 2021, themeontology.org
import os.path
import sys
from pathlib import Path

import themeontology


class TestFunctionality:
    def test_to(self):
        """
        Test on data snapped from the ontology.
        """
        print("")
        for path in sys.path:
            if os.path.isfile(os.path.join(path, "themeontology.py")):
                lib.log.info("Project Path: %s", path)
        to = themeontology.read(path)
        for warning in to.validate():
            print(warning.encode("ascii", "replace"))

    def test_cycle_warning(self):
        """
        Ensure we get warnings about theme cycles.
        """
        to = themeontology.read("data/tests/cycles1.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1
        to = themeontology.read("data/tests/cycles2.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1
        to = themeontology.read("data/tests/cycles3.th.txt")
        assert len([msg for msg in to.validate() if "Cycle:" in msg]) == 1

