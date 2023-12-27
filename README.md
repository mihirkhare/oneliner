**Oneliner - Translate any Python 3 program to a single line expression, no statements at all**
*(ideally, not yet sure of any limits)*

Inspired by my single line submission to 15-451's Homework 7.5 programming assignment in Fall 2023.

~~There are 2 main planned translation options: one that uses a list to act as the variable store with commas for program flow, and another that uses lambdas for variable binding with continuations for program flow. I believe these should both have equivalent functionality, but its possible some loosening may be required.~~ In implementing a continuation transformation for variable binding, I discovered a bug/issue with the CPython parser, where it raises a MemoryError while parsing a ~1000 nested lambda expression (see `exploration/recdepth.py`). To avoid having to use deep nested lambdas for variables, I instead use the `globals()` and `locals()` dictionaries to add/delete variables from a scope. This is essentially equivalent to the list method, so only 1 real implementation will be created. A second (trivial) option will turn the input program into a string and use `exec` - this is really just available for completeness.

**Planned Translations:**
- Variables
- Scoping
- Expressions
- Conditionals
- Loops
- Functions (including recursion)
- Imports
- Classes
- Raising exceptions

**Not-sure-if-possible Translations:**
- Multi-file programs
- Handling exceptions (`try`-`except` blocks)
- `with` statements
- Likely more (to be discovered as I go on)