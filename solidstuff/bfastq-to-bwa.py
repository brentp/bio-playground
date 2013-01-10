import sys
import string

encoder = string.maketrans('0123.', 'ACGTN')

for i, line in enumerate(sys.stdin, start=0):
    if i % 4 == 1:
        # double encode sequence
        assert line[0] == "T"
        print line[2:-1].translate(encoder)
    elif i % 4 == 3:
        # drop first qual
        print line[1:],
    else:
        print line,
