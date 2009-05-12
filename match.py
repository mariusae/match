"""A destructing pattern matcher for Python, inspired by all manners
of functional programming languages!

  >>> from util.match import M, A, A_

  M  - destructuring match-expression, ~M pure match expression
  A  - argument for destructuring -- specify # by `/'-operator
  A_ - any-argument

With `M', you build a match-expression, eg.

  >>> ~M((1, (A_, 3), A/1, A/0))

This represents the pattern itself, a match-expression is useless
until it is _bound_. You can bind them with the `==' operator. Eg.:

  >>> ~M((1, (A_, 3), A/1, A/0)) == (1, (2, 3), 1, 2)
  True

The `==' operator _destructures_ the match if the `~' is dropped.

  >>> M((1, (A_, 3), A/1, A/0)) == (1, (2, 3), 1, 2)
  (2, 1)

Now, to make it more interesting, match-expressions can be or-ed
together, resulting in the first match. This is the typical use of the
pattern-matching aspect of destructuring matching:

  >>> M([A/0]) | M(A/0) == [5]
  5
  >>> M([A/0]) | M(A/0) == 5
  5

Note that, as in all destructuring systems, order is very
important. For example, imagine this:

  >>> M([A/0]) | M(A/0) | M([1, A/0]) == [1, -10]
  [1, -10]

Here, the second match-expression catches it (since A/0 will match
anything), and our intent was most likely to have this match the third
case:

  >>> M([A/0]) | M([1, A/0]) | M(A/0) == [1, -10]
  -10

TODO: add support for dicts, sets and pystructs.

TODO: add support for head/rest for dicts and structs

TODO: actually distinguish between binding vs. non-binding args, and
allow them to repeat, eg.:

   M([A/0, A/0, A_])

would require both A/0s to be equivalent.

Match-expressions also support a *default* argument that can be used
to return a different value if the expression matches. This can be
handy for dealing with polymorphic return values, eg. for array
slicing:

  >>> M([A/0]) | M([], d=False) == arr[:1]

here, if arr contains one element, we pick it; if it's empty, we
return `False'."""

from itertools import chain
import types

__all__ = ['M', 'A', 'A_']

class _Arg(object):
    def __init__(self, argn=None, value=None):
        self.value = value
        self.argn = argn

    def __div__(self, other):
        return _Arg(argn=other)

    def bind(self, value):
        return _Arg(argn=self.argn, value=value)

A_ = _Arg()
A = _Arg()

def match(p, v):
    if isinstance(p, _Arg):
        return True, [p.bind(v)]

    t = type(p)

    if not isinstance(v, t):
        return False, []

    if p == v:
        return True, []
    elif t == types.ListType or t == types.TupleType:
        if len(p) != len(v):
            return False, []
        else:
            def combine((x, y), (a, b)):
                if not x:
                    return x, y
                else:
                    matched, matches = match(a, b)
                    if matched:
                        return True, (y + matches)
                    else:
                        return False, y

            return reduce(combine, zip(p, v), (True, []))
    else:
        return False, []


def match_and_bind(p, v):
    matched, matches = match(p, v)
    if not matched:
        return None
    else:
        return tuple(map(lambda x: x.value,
                         sorted(filter(lambda x: x.argn is not None, matches),
                                key=lambda x: x.argn)))


class M(object):
    def __init__(self, pattern, **kwargs):
        self.pattern = pattern
        self.matches = []
        self.has_d = 'd' in kwargs
        if self.has_d:
            self.d = kwargs.pop('d')

        self.destruct = True

    def __invert__(self):
        self.destruct = False
        return self

    def __eq__(self, other):
        return self.match(other)

    def match(self, value):
        for m in chain(reversed(self.matches), [self]):
            res = match_and_bind(m.pattern, value)
            if res is None:
                continue
            elif not m.destruct:
                return True
            elif m.has_d:
                return m.d
            else:
                return res
        else:
            if self.destruct:
                raise ValueError, 'No match for %s' % value
            else:
                return False

    def _append(self, others):
        self.matches.extend(others)

    def __or__(self, other):
        # left-to-right, so prefer self.
        other._append([self] + self.matches)
        return other
