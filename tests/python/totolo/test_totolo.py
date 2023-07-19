# Copyright 2021, themeontology.org
import totolo


class TestFunctionality:
    def test_to(self):
        """
        Test on data snapped from the ontology.
        """
        to = totolo.remote()
        to.print_warnings()

    def test_cycle_warning(self):
        """
        Ensure we get warnings about theme cycles.
        """
        to = totolo.files("data/tests/cycles1.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("data/tests/cycles2.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("data/tests/cycles3.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
