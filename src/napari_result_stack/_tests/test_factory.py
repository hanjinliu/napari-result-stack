import pytest

from napari_result_stack.factory import WidgetFactoryMap


def test_dict_methods():
    fact = WidgetFactoryMap()
    assert len(fact) == 0
    fact[str] = lambda x: None
    assert len(fact) == 1
    with pytest.raises(TypeError):
        fact[float] = 0
    del fact[str]
    assert len(fact) == 0


def test_register():
    fact = WidgetFactoryMap()
    assert len(fact) == 0
    fact.register(int, lambda x: None)

    @fact.register(float)
    def f(x):
        pass

    @fact.register
    def g(x: float):
        pass

    with pytest.raises(TypeError):
        fact.register(float, 0)

    with pytest.raises(TypeError):
        fact.register()

    with pytest.raises(TypeError):
        fact.register(float, lambda x: None, 0)
