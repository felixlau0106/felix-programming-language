# Felix's Programming Language - FPL

> **Working title.** The name may change while the language and compiler are in development.

## Current Progress

Finished Lexer and Parser. Working on Semantic Analyzer. 

## Key ideas

- **Functions** require explicit argument types and a return type, so a reader can understand a function from its header.
- **Locals** are self-explaining: if the value already shows the type, you are not forced to write it. `x = 5` is enough; `x: int = 5` is still allowed.
- **Pitch:** Python simplicity without indentation-as-syntax, TypeScript-ish type clarity without braces, C performance (FPL transpiles to C).

## Code example

```fpl
# main.fpl
# Triple-quoted strings (""" ... """) are not supported yet.

def add_nums(a: int, b: int): int
    return a + b
end

def minus_nums(a: int, b: int): int
    return a - b
end

def main(): int
    x = 5
    y = 12
    z = add_nums(x, y)

    if z > 10:
        say(str(z) + " is greater than 10.")
    elif z == 10:
        say(str(z) + " is 10.")
    else:
        say(str(z) + " is less than 10.")
    end

    num = 0

    while num < 20:
        num = add_nums(num, 1)
    end

    say(num)

    return 0
end
```

Semicolons are treated as newlines, so one-liners are *allowed, not blessed*. (Go and Swift make spaghetti one-liners hard on purpose. Please don't.)

```fpl
def add(a: int, b: int): int return a + b end; x = 5; y = 10; say(add(x, y))
```

## Basic syntax

### Variables

```fpl
a = 5
b = "Felix"
c = 5.123456789
# or, when you want to shout the type:
x: int = 5
y: str = "Felix"
z: double = 5.123456789
```

Lists / tuples / dicts are **not implemented** in the compiler yet (old notes):

```fpl
# planned / maybe
li: list = []
li.push("string")
say(li[1])

arr = (5, 6, 7, 8)
dict = {"a": 1, "b": 2}
```

### Functions

```fpl
def function_name(arg1: int, arg2: int): int
    arg3 = 4
    return arg1 + arg2 + arg3
end

def function_with_no_return(): void
    say("Hello world!")
end

# main returns int, like C
def main(): int
    return 0
end
```

### If

Python-shaped condition (`:` after the cond), Ruby-shaped closer (`end`) — not `endif`.

```fpl
if a > b:
    say("a is bigger than b.")
elif a == b:
    say("a and b are the same.")
else:
    say("b is bigger than a.")
end
```

### While

```fpl
while num < 20:
    num = add_nums(num, 1)
end
```

### And, or, not

Plain English (uppercase is also fine):

```fpl
if (a > 0 and a > b):
    say("a is bigger than b and zero.")
end

if (y < 0 or z < 0):
    say("y or z is smaller than zero.")
end

if not (c > 0):
    say("c is not bigger than zero.")
end
```

### Comments

```fpl
# This is a comment
x: int = 5  # this works too
```

Block comments / `"""` strings — later.

### Built-in functions

```fpl
say("Hello")
say(5)
say(var_x)
# mixing several types in one say() — not yet
```

User input (`ask`) — **not implemented yet**.

```fpl
# planned
age: int = ask()
```

### directc

Escape hatch: real C between `directc"""` and `"""`, then `end`. **No parentheses.**

```fpl
def main(): int
    directc"""
    printf("Hello world!"); /* any normal C */
    return 0;
    """
    end
end
```

## CLI (planned)

```text
fpl build main.fpl    # transpile to C, then compile with the system C compiler
fpl run main.fpl      # compile into a temp cache, run the binary
fpl repl              # REPL
```

Example:

```text
fpl repl
repl> say("Hello, world!")
Hello, world!
repl> 1 + 1
2
repl>
```
