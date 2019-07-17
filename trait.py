from common import classproperty
from typing import Dict, Type, Dict


# TODO mm, that should only be stored in target trait!!!
class AbsTrait:
    Target: Type = NotImplemented

    # TODO how to refer to target here??
    _impls: Dict[Type, Type['AbsTrait']] = NotImplemented

    @classmethod
    def reg(cls, *traits: Type['AbsTrait']):
        for tr in traits:
            cls._impls[tr.Target] = tr # TODO check for existence?

    @classmethod
    def for_(cls, f):
        if not isinstance(f, type): # TODO eh?
            f = type(f)
        return cls._impls[f]

def pull(mref):
    Trait = mref.__self__
    name = mref.__name__
    def _m(obj, *args, **kwargs):
        Dispatched = Trait.for_(obj)
        return getattr(Dispatched, name)(obj, *args, **kwargs)
    return _m

# https://stackoverflow.com/a/3655857/706389
def islambda(v):
    LAMBDA = lambda:0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__


def test():
    from typing import NamedTuple
    class A:
        x = 123

    class B:
        z = "string!"

    class L:
        x = 'smth lazy'


    class ShowTrait(AbsTrait):
        _impls = {}

        @classmethod
        def show(trait, obj, *args, **kwargs):
            raise NotImplementedError


    # TODO square brackets?
    class _For:
        def __getitem__(self, cls):
            class ForCls:
                @classproperty # TODO can be static prop?
                def Target(ccc, cls=cls):
                    if islambda(cls):
                        cc = cls()
                    else:
                        cc = cls
                    return cc
            return ForCls

    For = _For()

    show = pull(ShowTrait.show) # TODO ?
    class ForA:
        @classproperty
        def Target(cls):
            return A

    class ShowA(ForA, ShowTrait):
        @classmethod
        def show(trait, obj, *args, **kwargs):
            return f'A containing {obj.x}'

    class ShowB(For[B], ShowTrait):
        @classmethod
        def show(trait, obj, *args, **kwargs):
            return f'I am {obj.z}'

    ForL = For[lambda: L] # TODO eh, capturing?
    class ShowL(ForL, ShowTrait):
        @classmethod
        def show(trait, obj, *args, **kwargs):
            return 'showl'

    ShowTrait.reg(ShowA, ShowB, ShowL)


    assert show(A()) == 'A containing 123'
    assert show(B()) == 'I am string!'
    assert show(L()) == 'showl'

    assert show(A()) == 'A containing 123'
    assert show(B()) == 'I am string!'
    assert show(L()) == 'showl'
