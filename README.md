# Lily
See dev-branch for actual version

Lily is a Lotus interpreter implementation. It is a prototype!

Generally, Lotus - is my own compilation of wishes about Python. Lily is an ethelon implementation of it (cause it is the only implementation, heh)

What about future plans - I wanna write a llvm-compiler for Lotus. But it will not be soon.

New features: added scopes. What I mean? previously, I had only 1 context for all the objects. This branch contains a version, which fixes that shit, so functions and classes has different and independent scopes.

Lotus also now supports python objects using. Calling, printing values, importing modules, using OOP.


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
  return a + b + c
}

func five() {
  return 5
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
Imports (native):
```
import 'path/to/package' as package  # full path to my_package is ./path/to/package.lt

print(package.description)  # for example
```
---
Imports (python modules):
```
pyimport 'path.to.package' as package
# here we say python-like path to module
# pyimport statement uses importlib.import_module

print(package.__description__)
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
    return cls.a + cls.b
  }
}

my_class = MyClass(1, 2)
print(my_class.get_sum())  # output: 3
```

cls: class instance (can be named, as you want. `self`, for example, or `this`)

Actually, in theory, classes also supports all the python's operators overloading. But I haven't tested it yet
---
Built-in Python objects' bindings:
```
print(*args, end='\n', sep=' ') - text output
input(string) - text input
true - True (will be changed soon)
false - False (will be changed soon)
null - None
getattr, setattr, hasattr - see in python docs*
import_py_module(python_like_path) - bind to the importlib.import_module
```
---
Lists:
```
my_list = [1, 2, 3]
print(my_list + [4])  # output: [1, 2, 3, 4]
my_list.append(4, 5)  # my_list now: [1, 2, 3, 4, 5]
my_list.extend([6, 7], [8, 9])  # my_list now: [1, 2, 3, 4, 5, 6, 7, 8, 9]
print(my_list.contains(6))  # True
print(my_list.get(5))       # get element with index 5. 6 will be printed
print(my_list.length)       # returns 9, cause list contains 9 elements
```
---
Dicts: 
```
my_dict = {
  'one': 1,
  'two': 2,
  'three': 3
}

my_dict_items = my_dict.items()  # returns list, which contains lists [key, value]

# prints smth like "one: 1"
for (i=0; i<my_dict_items.length; i=i+1) {
  (key, value) = my_dict_items[i]  # look at this! This is variable unpacking!
  print(key, ': ', value, sep='')
}
```
---
Variables unpacking (showed in the example above):
```
my_list = [1, 2, 3]
(one, two, three) = my_list
```
To unpack variables, you should write names in a braces. Works as in python, so, list should contain as much values, as variables you're declaring
---
Eval/exec statements:
```
exec "func my_func(a, b, c) { return (a + b + c) }"
print(my_func(1, 2, 3))  # output: 6

print(eval "1+2+3")  # output: 6

# argument also may be a variable
code = "print('it\'s Wednesday, dudes')"
exec code

# exec/eval made by operators cuz I need to pass context to them
```
