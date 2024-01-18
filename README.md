# dict2any

[![PyPI - Version](https://img.shields.io/pypi/v/dict2any.svg)](https://pypi.org/project/dict2any)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dict2any.svg)](https://pypi.org/project/dict2any)

---

Problem: You need to initialize a nested data structure (such as a dataclass containing another dataclass)

Solution: use `dict2any.parse(MyClass, data)` and it will recursively build up your data structure using type hints.

# Usage

```python
from dataclasses import dataclass
from dict2any import parse

@dataclass
class Package:
  name: str

@dataclass
class Config:
  packages: list[Package]

config = parse(Config, {"packages": [{"name": "wow"}, {"name": "amazing"}]})
print(config)
# Config(packages=[Package(name='wow'), Package(name='amazing')])
```

# Advanced usage

## Custom Parsing

The `parsers`argument lets you pass in additional parsers, to further customize or extend the functionality.

To do so, you must implement the [Parser](./dict2any/parsers/parser.py) protocol. There are two methods: `can_parse`, and `parse` which you should implement. Take a look at any of the [builtin parsers](./dict2any/parsers/) for inspiration

### Implementing can_parse

The first parser which returns `True` to `can_parse` is the one that wins, and will parse that data type. Instead of a strict ordering (e.g try the DictParser, then the ListParser, etc etc.), the algorithm works in stages. It is expected that only one parser will match for a data type for a given stage. The stages are as follows:

- Override: This stage is checked first. No builtin parsers use this stage. Instead, it's an opportunity for any custom parsers to "win" and be the one chosen to parse a data type
- Exact: This parser knows how to parse this exact data type. For example, a certain class, or when an object `is` a certain type
- Fallback: The parser is a little more generic, and handles subclasses or other coerceable classes.
- LastChance: Generically try to handle all classes

For example, the [DictParser](./dict2any/parsers/dict.py) can_parse the following types in `Stage.Exact`:

- dict
- OrderedDict
- dict[str, str]

and it can additionally parse the following types in `Stage.Fallback`:

- TypedDict
- UserDict
- class MyDict(dict)
- Any class which implements collections.abc.Mapping or collections.abc.MutableMapping

## Alternative solutions

- [pydantic](https://pypi.org/project/pydantic/) (tons of features)
- [dataclass-wizard](https://pypi.org/project/dataclass-wizard/) (only for dataclasses)
