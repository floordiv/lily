# Lily
Lily is a Lotus interpreter implementation. It is a prototype!

Generally, Lotus - is my own compilation of wishes about Python. Lily is an ethelon implementation of it (cause it is the only implementation, heh)

What about future plans - I wanna write a llvm-compiler for Lotus. But it will not be soon.

New features: added scopes. What I mean? previously, I had only 1 context for all the objects. This branch contains a version, which fixes that shit, so functions and classes has different and independent scopes


---
## So, short documentation:

Arithmetic:
```
# works identically to python, but some are differ. Differs:
print(false || true)  # OR operation
print(true && true)   # AND operation
print(!true)          # NOT operation
```
---
Comments:
```
# interpreter won't see this :)
```
---
Variables and datatypes:
```
int = 5
float = 5.5
bool = true
null_var = null
string = 'hello, world!'
string_doublequotes = "Mark's string is there"
```
---
Branches:
```
if (some_expression) {
  # some code
} elif (some_another_expression) {
  # some code
} else {
  # some code
}
```
---
Functions:
```
func sum_abc(a, b, c) {
  return (a + b + c)  # yes, to return values, we use braces
}

func five() {
  return 5  # but for single element, we may not use it
}

my_sum = sum_abc(1, 2, 3)
print('Sum of 1, 2, 3:', my_sum)  # works identically as python's analog
print("Five:", five())
```
---
Extended functions example:
```
func equals_to_seven_or_custom(source, equals_to=7) {
  # all this may be shortened to `return source == equals_to`
  # but c'mon, this is a language demostration
  
  if (source == equals_to) {
    return true
  } else {
    return false
  }
}
```
---
For-loops:
```
# works identically to the C variant
for (a=0; a<5; a=a+1) {
  print(a)
}
```

Extended for-loops:
```
for (a=0; a<10, a=a+1) {
  if (a == 3 || a == 5 || a == 7) {
    continue
  } elif (a == 9) {
    break
  }
  
  print(a * 10)
}
```
---
While-loops:
```
while (expression) {
  # do code
}
```
For example:
```
i = 0

while (i < 10) {  # break and continue statements also work here
  print(i * 10)
  i = i + 1
} print(100)
```
---
Imports:
```
import 'path/to/package' as my_package  # full path to my_package is ./path/to/package.lt
print(my_package.package_description)  # for example
```
---
Classes:
```
class MyClass {
  func __init__(cls, a, b) {
    cls.a = a
    cls.b = b
  }
  
  func get_sum(cls) {
    return (cls.a + cls.b)
  }
}

my_class = MyClass(1, 2)
print(my_class.get_sum())  # output: 3
```

cls: class instance (can be named, as you want. `self`, for example, or `this`)

Actually, in theory, classes also supports all the python's operators overloading. But I haven't tested it yet
