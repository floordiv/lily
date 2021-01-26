import lib.std.ljson as json


simple_json = """
{
"one": 1,
"two": 2,
5: [1, 2, 3],
6: {"six": 6},
7: true,
8: false,
9: null,
}
"""
print(json.parse(simple_json))
