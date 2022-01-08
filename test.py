import hash
import time

str = "There's plenty for the both of us, may the best Dwarf win."
start = time.time()
out = hash.gimli(str)
output = out.replace(" ", "")
end = time.time()
print(output)
print(end - start)