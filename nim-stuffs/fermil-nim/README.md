[fermi-lite](https://github.com/lh3/fermi-lite/) wrapper for nim.

Allows assembling short reads.

```Nim
  import fermil
  var dna = "AAAAACTCTACCTCTCTATACTAATCTCCCTACAAATCTCCTTAATTATAACATTCACAGCCACAGAACTAATCATATTTTATATCTTCTTCGAAACCAC"
  var qual = "2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222"

  var fml = new_fermi()
  var i = 0
  # example adding some sub strings of the above sequence...
  while i <= (dna.len - 80 + 3):
    var s = dna[i..<(i+80)]
    var q = qual[0..<s.len]
    # quality is optional.
    fml.add(s, q)
    i += 3

  var tigs = fml.assemble()
  echo dna
  echo tigs[0].seq
  echo len(tigs)

  # or
  for unitig in tigs:
     echo unitig.len    
```


# NOTE

because of nim's garbage collector, this contains a slightly modified version of fermi-lite short
that nim is responsible for cleaning up the sequences rather than having them `free'd` inside of `fermi-lite`
