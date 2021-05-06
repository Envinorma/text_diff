# Text Diff

[![Build Status](https://github.com/envinorma/text_diff/workflows/Build%20Main/badge.svg)](https://github.com/envinorma/text_diff/actions)
[![Documentation](https://github.com/envinorma/text_diff/workflows/Documentation/badge.svg)](https://envinorma.github.io/text_diff/)
[![Code Coverage](https://codecov.io/gh/envinorma/text_diff/branch/main/graph/badge.svg)](https://codecov.io/gh/envinorma/text_diff)

Python diffline wrapper.

---

## Quick Start

```python
from text_diff import text_differences

text_1 = [
    'Hello',
    'World',
    'How are you ?',
]

text_2 = [
    'Hello',
    'World!',
    'How are u ?',
]

diff = text_differences(text_1, text_2)
for line in diff.diff_lines:
    print(type(line))
```

## Installation

**Stable Release:** `pip install text_diff`<br>
**Development Head:** `pip install git+https://github.com/envinorma/text_diff.git`

## Documentation

For full package documentation please visit [envinorma.github.io/text_diff](https://envinorma.github.io/text_diff).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

**MIT license**
