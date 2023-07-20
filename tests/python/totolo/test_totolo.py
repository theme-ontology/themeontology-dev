import totolo


class TestCreation:
    def test_empty(self):
        to = totolo.empty()
        assert len(to) == 0

    def test_remote_head(self):
        to = totolo.remote()
        to.print_warnings()
        assert len(to) > 3

    def test_remote_version_old(self):
        to = totolo.remote.version("v0.3.3")
        to.print_warnings()
        assert len(to) > 3

    def test_remote_version_new(self):
        to = totolo.remote.version("v2023.06")
        to.print_warnings()
        assert len(to) > 3


class TestValidation:
    def test_cycle_warning(self):
        to = totolo.files("data/tests/cycles1.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("data/tests/cycles2.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("data/tests/cycles3.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
