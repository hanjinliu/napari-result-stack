from magicgui import magicgui

from napari_result_stack.types import StoredMeta


def test_store_result(stored: StoredMeta):
    @magicgui
    def f(x: int) -> stored[int]:
        return x

    assert list(stored.valuesof[int]) == []
    f(1)
    assert list(stored.valuesof[int]) == [1]
    f(2)
    assert list(stored.valuesof[int]) == [1, 2]


def test_receiving_stored_values(stored: StoredMeta):
    @magicgui
    def provide(x: int) -> stored[int]:
        return x

    @magicgui
    def receive(x: stored[int]):
        return x + 1

    assert list(stored.valuesof[int]) == []
    assert receive.x.choices == ()

    provide(1)
    assert list(stored.valuesof[int]) == [1]
    assert receive.x.choices == (1,)
    assert receive() == 2

    provide(2)
    assert list(stored.valuesof[int]) == [1, 2]
    assert receive.x.choices == (1, 2)


def test_independency(stored: StoredMeta):
    @magicgui
    def provide_0(x: int) -> stored[int, 0]:
        return x

    @magicgui
    def receive_0(x: stored[int, 0]):
        return x + 1

    @magicgui
    def provide_1(x: int) -> stored[int, 1]:
        return x

    @magicgui
    def receive_1(x: stored[int, 1]):
        return x + 1

    assert list(stored.valuesof[int, 0]) == []
    assert list(stored.valuesof[int, 1]) == []
    provide_0(-1)
    assert list(stored.valuesof[int, 0]) == [-1]
    assert list(stored.valuesof[int, 1]) == []
    provide_1(-2)
    assert list(stored.valuesof[int, 0]) == [-1]
    assert list(stored.valuesof[int, 1]) == [-2]

    assert receive_0.x.choices == (-1,)
    assert receive_1.x.choices == (-2,)


def test_list_like_methods(stored: StoredMeta):
    stored[str]
    stored.valuesof[str].append("a")
    stored.valuesof[str].append("b")
    stored.valuesof[str].append("c")
    assert list(stored.valuesof[str]) == ["a", "b", "c"]
    stored.valuesof[str].pop(1)
    assert list(stored.valuesof[str]) == ["a", "c"]


def test_overflow(stored: StoredMeta):
    stored[str]
    stored.valuesof[str].maxsize = 3
    assert stored.valuesof[str].maxsize == 3
    stored.valuesof[str].append("a")
    stored.valuesof[str].append("b")
    stored.valuesof[str].append("c")
    assert list(stored.valuesof[str]) == ["a", "b", "c"]
    stored.valuesof[str].append("d")
    assert list(stored.valuesof[str]) == ["b", "c", "d"]
    stored.valuesof[str].append("e")
    assert list(stored.valuesof[str]) == ["c", "d", "e"]


def test_setting_overflow(stored: StoredMeta):
    stored[str]
    stored.valuesof[str].append("a")
    stored.valuesof[str].append("b")
    stored.valuesof[str].append("c")
    assert list(stored.valuesof[str]) == ["a", "b", "c"]
    stored.valuesof[str].maxsize = 1
    assert list(stored.valuesof[str]) == ["c"]
    stored.valuesof[str].append("b")
    assert list(stored.valuesof[str]) == ["b"]
