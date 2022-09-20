from rxflow.elements import Var, Seq, Fn, Val
from decimal import Decimal as d
import pytest
import asyncio


class TestElementsExist:
    def test_var(self):
        p1 = Var(d(3))
        p2 = Var(d(2))
        sum = p1 + p2
        assert sum == Var(d(5))

    def test_str_var(self):
        p1 = Var("hello")
        p2 = Var(2)
        mul_str = p1 * p2
        assert mul_str == Var("hellohello")

    def test_fn(self):
        a = Var(1)
        b = Var(1)
        c = Var(-10)

        def compute_roots(a, b, c):
            discriminant = (b**2) - (4 * a * c)
            if discriminant < 0:
                raise ArithmeticError("no roots exist")
            d = (discriminant**0.5) / (2 * a)
            return (-b + d, -b - d)

        def double_tuple(p):
            return (p[0] * 2, p[1] * 3)

        d1 = Fn(compute_roots, a=a, b=b, c=c)
        d2 = Fn(double_tuple, p=d1)

        c(-15)

    def test_seq(self):
        def fibber(fib, fib0, fib1):
            def fibbr(n):
                if n == 0:
                    return fib0
                elif n == 1:
                    return fib1
                else:
                    return fib[n - 1] + fib[n - 2]

            return fibbr

        v0 = Var(0)
        v1 = Var(1)
        vx = Fn(lambda x: x + 1, x=v0)

        c1 = Seq(fibber, fib0=vx, fib1=v1)

        assert c1[10] == 89

        v0(1)

        assert c1[10] == 123

    def test_fib_seq(self):
        def fibber(fib, fib0, fib1):
            def fibbr(n):
                if n == 0:
                    return fib0
                elif n == 1:
                    return fib1
                else:
                    return fib[n - 1] + fib[n - 2]

            return fibbr

        v0 = Var(0)
        v1 = Var(1)
        fib = Seq(fibber, fib0=v0, fib1=v1)

        assert fib[5] == 5
        assert fib[8] == 21

        v0(15)

        assert fib[2] == 16

    @pytest.mark.asyncio
    async def test_async_fn(self):

        price = Var(10)

        async def plus_1_async(n):
            await asyncio.sleep(1)
            return n + 1

        res = Fn(plus_1_async, n=price)
        k = await res()


class TestElementsAreReactive:
    def test_create_var(self):
        a = Var(10)
        assert a

    def test_dereference_var(self):
        a = Var(10)
        assert Val(a) == 10

    def test_create_fn(self):
        a = Var(10)
        b = Var(5)
        c = Fn(lambda a, b: a * b, a=a, b=b)
        assert c

    def test_evaluate_fn(self):
        a = Var(10)
        b = Var(5)
        c = Fn(lambda a, b: a * b, a=a, b=b)
        assert type(Val(c)) == int

    def test_fn_evaluates_correctly(self):
        a = Var(10)
        b = Var(5)
        c = Fn(lambda a, b: a * b, a=a, b=b)
        assert 10 * 5 == Val(c)

    def test_var_equality(self):
        a = Var(10)
        b = Var(5)
        c = Fn(lambda a, b: a * b, a=a, b=b)
        assert c == Var(Val(c))

    def test_update_var(self):
        a = Var(10)
        assert Val(a) == 10

        a(16)
        assert Val(a) == 16

    def test_update_fn(self):
        a = Var(10)
        b = Var(5)
        c = Fn(lambda a, b: a * b, a=a, b=b)
        assert 10 * 5 == Val(c)

        a(15)

        assert 15 * 5 == Val(c)

    def test_create_seq(self):
        fib0 = Var(0)
        fib1 = Var(1)

        def fibbr(N, fib0, fib1):
            def _fibbr(n):
                if n == 0:
                    return fib0
                elif n == 1:
                    return fib1
                else:
                    return N[n - 1] + N[n - 2]

            return _fibbr

        fibn = Seq(fibbr, fib0=fib0, fib1=fib1)
        assert fibn[0] == Val(fib0)
        assert fibn[1] == Val(fib1)
        assert fibn[2] == Val(fib0) + Val(fib1)

    def test_update_seq(self):
        fib0 = Var(0)
        fib1 = Var(1)

        def fibbr(N, fib0, fib1):
            def _fibbr(n):
                if n == 0:
                    return fib0
                elif n == 1:
                    return fib1
                else:
                    return N[n - 1] + N[n - 2]

            return _fibbr

        fibn = Seq(fibbr, fib0=fib0, fib1=fib1)

        assert fibn[4] == 3

        fib0(1)

        assert fibn[4] == 5


class TestElementsAreObservable:
    def test_var_observer(self):

        a = Var(0)
        calls = []

        def on_updated(path, var, prev, next):
            calls.append([path, var, prev, next])

        a.on_change.add(on_updated)

        a(14)
        a(18)

        a.on_change.remove(on_updated)

        assert len(calls) == 2
        assert calls[0] == [None, a, 0, 14] and calls[1] == [None, a, 14, 18]

    def test_fn_observer(self):

        a = Var(0)
        b = Var(5)

        c = Fn(lambda a, b: (a * b) + 5, a=a, b=b)
        calls = []

        def c_changed(key, var, prev, next):
            calls.append([key, var, prev, next])

        c.on_change.add(c_changed)

        a(14)
        b(18)

        c.on_change.remove(c_changed)

        assert len(calls) == 2
        assert calls[0] == ["a", a, 0, 14] and calls[1] == ["b", b, 5, 18]

    def test_seq_observer(self):
        def fibber(fib, fib0, fib1):
            def fibbr(n):
                if n == 0:
                    return fib0
                elif n == 1:
                    return fib1
                else:
                    return fib[n - 1] + fib[n - 2]

            return fibbr

        v0 = Var(0)
        v1 = Var(1)
        vx = Fn(lambda x: x + 1, x=v0)

        c1 = Seq(fibber, fib0=vx, fib1=v1)

        calls = []

        def c1_changed(key, var, prev, next):
            calls.append([key, var, prev, next])

        c1.on_change.add(c1_changed)

        v0(3)

        v1(6)

        c1.on_change.remove(c1_changed)
        v1(4)

        assert len(calls) == 2
        assert calls[0] == ["fib0.x", v0, 0, 3] and calls[1] == ["fib1", v1, 1, 6]
