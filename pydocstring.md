# Docstring Conventions (PEP 257)

- [PEP 257](https://raw.githubusercontent.com/python/peps/refs/heads/main/peps/pep-0257.rst)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Google docstring style example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

## General

- use triple quotes, and _raw_ triple quotes if doc contains backslash

### One-Liner

"""Prescribe function's effect in <= 80 characters ending in a period."""

"""Prescribe a function's effect (as an imperative phrase) and describe the
   value it returns (if relevant) ending in a period."""

### Multi-Liner

"""
Unless the entire docstring fits on a line, place the closing quotes
on a line by themselves.  This way, Emacs' ``fill-paragraph`` command
can be used on it.

class DocsDemo:
"""

## Script

- should be usable as its "usage" message
- should document the script's function and command line syntax,
  environment variables, and files
- should be sufficient for a new user to use the command properly
- should provide a sophisticated user with a complete quick reference
  to all options and arguments

## Package

- should list the modules and subpackages exported by the package

## Module

- all

- should generally list the classes, exceptions, and functions
 exported by the module, with a one-line summary of each

## Class

- all public

- should summarize class's behavior
- should list public instance variables, but not @propertys

class Demo:

The docstring for a class should summarize its behavior and list the
public methods and instance variables.  If the class is intended to be
subclassed, and has an additional interface for subclasses, this
interface should be listed separately (in the docstring).  The class
constructor should be documented in the docstring for its ``__init__``
method.  Individual methods should be documented by their own
docstring.

Insert a blank line after all docstrings (one-line or multi-line) that
document a class -- generally speaking, the class's methods are
separated from each other by a single blank line, and the docstring
needs to be offset from the first method by a blank line.

If a class subclasses another class and its behavior is mostly
inherited from that class, its docstring should mention this and
summarize the differences.  Use the verb "override" to indicate that a
subclass method replaces a superclass method and does not call the
superclass method; use the verb "extend" to indicate that a subclass
method calls the superclass method (in addition to its own behavior).

## Function / Method

- all public

The docstring for a function or method should summarize its behavior
and document its arguments, return value(s), side effects, exceptions
raised, and restrictions on when it can be called (all if applicable).
Optional arguments should be indicated.  It should be documented
whether keyword arguments are part of the interface.

Raises:

List all exceptions that are relevant to the interface followed by a
description. Use a similar exception name + colon + space or newline
and hanging indent style as described in Args:. You should not
document exceptions that get raised if the API specified in the
docstring is violated (because this would paradoxically make behavior
under violation of the API part of the API).

```python
    def add(x: int, y: int) -> int:
    """{Prescriptive one-liner ending in a period.}

    {A docstring should give enough information to write a call to the
    function without reading the function’s code. The docstring should
    describe the function’s calling syntax and its semantics, but
    generally not its implementation details, unless those details are
    relevant to how the function is to be used. For example, a function
    that mutates one of its arguments as a side effect should note that in
    its docstring. Otherwise, subtle but important details of a function’s
    implementation that are not relevant to the caller are better
    expressed as comments alongside the code than within the function’s
    docstring.}

    Args:
      {parameter name, indicating *variable_length or **keyword as needed}:
        {parameter description}
      {parameter name, indicating *variable_length or **keyword as needed}:
        {parameter description}

    Returns:  {or Yields: for generators}
      {describe the semantics of the return value
        - if function returns None, this section is not required
        - if function returns a tuple, describe as "A tuple (val_a, val_b),
          where val_a is ..., and val_b is ..."
      }

    Raises:
      {exception type}: {description}
    """
```

## TODO

- "attribute docstrings" ?
- "additional docstrings" ?
