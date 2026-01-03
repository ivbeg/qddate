from qddate import DateParser
import datetime

p = DateParser()

tests = [
    "7 August, 2015",
    "August 10th, 2015",
    "Wednesday 22 Apr 2015"
]

for t in tests:
    print(f"Testing '{t}': ", end="")
    try:
        res = p.parse(t)
        print(f"Matched: {res}")
        if res:
            print(f"  Pattern: {p.match(t)['pattern']['key']}")
    except Exception as e:
        print(f"Error: {e}")
