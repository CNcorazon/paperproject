count = {}
value1 = '123'
value2 = 'dsf123'
value3 = '123'

if not value1 in count.keys():
    count[value1] = 1
else:
    count[value1] = count[value1] + 1


if not value2 in count.keys():
    count[value2] = 1
else:
    count[value2] = count[value2] + 1

if not value3 in count.keys():
    count[value3] = 1
else:
    count[value3] = count[value3] + 1


count = sorted(count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

print(str(count[0][1]))
