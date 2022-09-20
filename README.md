# rxflow

## Introduction

rxflow is minimalistic library for reactive state management in Python. It is inspired by derivablejs

## Features

- **Small, no dependencies** - Only 16KB of bytes of pure Pythonic goodness.

- **Push-pull change propagation** - Elements are observable and can send change notifications (push). Consumers can then lazily evaluate or dereference the changed element as needed (pull). This approach balances the amount of information in updates with the amount of computation triggered automatically on a variable changing.

- **Glitch-free** - Python evaluates from left to right producing a determinstic and glitch-free execution.

## Installation

Install rxflow by running:

    pip install rxflow

## Background and Motivation

> In computing, reactive programming is a declarative programming
> paradigm concerned with data streams and the propagation of change
> (Wikipedia)

In an imperative programming language like Python a variable assignment like `c = a * b` is instantaneous. `a` and `b` can be modified immediately after without affecting `c`

```py
>>> a = 10
>>> b = 5
>>> c = a * b
>>> print(c)
50
>>> b = 10
>>> print(c) ## This will still be 50
50
>>>
```

Procedural programming is a sensible default because it allows us to make many simplifying assumptions about variable naming and reuse. However, there are other cases where we may prefer that `c` updates dynamically based on the latest values of `a` and `b`. In other words, we want `c` to be **"reactive"** to `a` and `b`.

A spreadsheet is essentially a reactive programming interface because we can set some cell $X$ based on the value of one or more another cells $Y1..YN$ and any updates to $Y1..YN$ would automatically propagate to $X$. Both spreadsheets and reactive programming work well for use cases where we need to model lots of variables linked through a complex system of relationships. Solving such tasks procedurally is cumbersome and produces code that is difficult to reason about. rxflow is designed to brige this gap.

### Basic Example

```py
>>> from rxflow import Var, Fn, Val
>>> a = Var(10)
>>> b = Var(5)
>>> c = Fn(lambda a, b: a * b, a=a, b=b)
>>> print(Val(c))
50
>>> b(10)
>>> print(Val(c))  ## This will be 100 because b has changed
100
>>>
```

## Semantics

- There are 3 basic types of elements `Var` (variable), `Fn` (function) and `Seq` (sequence)
- A `Var` is the most basic type of element. A `Var` can be **created, updated** and **dereferenced**

  ```py
  from rxflow import Var, Val

  ## Create a Var
  pi = Var(3.1)
  print(pi)
  ## >> Var(3.1)

  ## Dereference a Var
  curr_pi = Val(pi)
  print(curr_pi)
  ## >> 3.1

  ## Dereference a Var
  pi(3.1415926535)
  print(Val(pi))
  ## >> 3.1415926535

  ```

- A `Fn` is a value that is derived from other elements. A `Fn` can be **created** and it's value can be **evaluated**

  ```py
  from rxflow import Var, Fn, Val

  pi = Var(3.141592)
  r = Var(42)

  ## Create a Fn from 2 Vars
  area = Fn(lambda pi, r: pi * pow(r, 2), pi=pi, r=r)

  ## Evaluate a Fn
  print(Val(area))
  ## >> 5541.768288

  ## Update one of the vars
  r(2048)

  print(Val(area))
  ## >> 13176791.891968
  ```

- A `Seq` is a sequence of values that are derived from other elements. A `Seq` can be **created** and it's values can be **accessed** by evaluating the generator.

  ```py
  from rxflow import Var, Seq

  def fibber(N, fib0, fib1):
      def fibbr(n):
          if n == 0:
              return fib0
          elif n == 1:
              return fib1
          else:
              return N[n - 1] + N[n - 2]
      return fibbr

  f0 = Var(0)
  f1 = Var(1)
  fib = Seq(fibber, fib0=f0, fib1=f1)

  print(fib[5])
  ## >> 5

  print(fib[8])
  ## >> 21

  print(fib[2])
  ## >> 16

  f0(15)

  print(fib[2])
  ## >> 16

  ```

  - **create** a `Seq` by calling `Seq(generator, **kwargs)`

    - `generator` is a function that takes `N: Seq, **args` and returns another function that accepts a single int `n` and returns the nth value in the sequence
    - `**kwargs` are the named arguments of type (`Union[Var,Fn,Seq]`) that will be passed to the generator

  - **access the elements** of a `Seq` e.g. `my_seq[42]`

## Contribute

- Issue Tracker: https://github.com/achadha235/rxflow/issues
- Source Code: https://github.com/achadha235/rxflow

## Support

If you are having issues, please let us know.
We have a mailing list located at: reactivepython@google-groups.com

## License

The project is licensed under the BSD license.
