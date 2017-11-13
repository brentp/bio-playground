import edlib_c
import strutils
type CArray{.unchecked.}[T] = array[0..0, T]

proc free(v: pointer) {.header: "<stdlib.h>", importc: "free".}

type
  Alignment* = ref object of RootObj
    ## Alignment wraps the result of align
    c*: EdlibAlignResult
  Config* = ref object of RootObj
    ## config determins the alignment parameters
    c*: EdlibAlignConfig

proc k*(c: Config): int =
  # return k window of the alignment config
  return c.c.k.int

proc mode*(c: var Config): EdlibAlignMode =
  # return the mode of the config
  return c.c.mode

proc new_config*(k:int=7, mode:EdlibAlignMode=EDLIB_MODE_HW, task:EdlibAlignTask=EDLIB_TASK_PATH): Config =
  ## create a new config object (this can not be modified as it's a copy)
  var cfg = edlibNewAlignConfig(k.cint, mode, task, nil, 0)
  return Config(c: cfg)

proc destroy_alignment(a: Alignment) =
  edlibFreeAlignResult(a.c)

proc cigar*(a:Alignment, s:var string, extended:bool=false): string =
  ## a string representation of the CIGAR
  var x = EDLIB_CIGAR_STANDARD
  if extended:
    x = EDLIB_CIGAR_EXTENDED
  var v = edlibAlignmentToCigar(a.c.alignment, a.c.alignmentLength, x)
  s = $v
  result = s
  free(v)

proc edit_distance*(a: Alignment): int {.inline.} =
  ## the edit distance between the target and the query.
  return a.c.editDistance

proc ok*(a: Alignment): bool {.inline.} =
  ## check that the alignment was actually performed.
  return a.c.status == EDLIB_STATUS_OK and a.edit_distance != -1

proc start*(a: Alignment): int =
  ## the first start of the alignment; negative for invalid alignment
  if a.c.startLocations == nil:
    return -1
  var arr = cast[ptr CArray[int]](a.c.startLocations.pointer)
  return arr[0]

proc length*(a: Alignment): int =
  return a.c.alignmentLength

proc alignTo*(query: string, target: string, config: Config): Alignment =
  ## align query to the target according to config.
  var a: Alignment
  new(a, destroy_alignment)
  # NOTE: should let user to upper
  a.c = edlibAlign(query.toUpperAscii.cstring, query.len.cint, target.toUpperAscii.cstring, target.len.cint, config.c)
  return a

const lookupt = ['-', '-', ' ', '-']
const lookupq = ['-', ' ', '-', '*']


proc score*(a:Alignment, match:int=1, mismatch:int=(-1), gap_open:int=(-2), gap_extend:int=(-1)): int =
  ## score an alignment. match should be positive and others should be negative.
  if a.c.alignment == nil:
    return -1
  var 
    arr = cast[ptr CArray[uint8]](a.c.alignment.pointer)
    ingap = false
  #if mismatch > 0: mismatch = -mismatch
  #if gap_open > 0: gap_open = -gap_open
  #if gap_extend > 0: gap_extend = -gap_extend

  for i in 0..<a.c.alignmentLength.int:
    var v = arr[i]
    if v == 0:
      ingap = false
      result += match
    elif v == 3:
      result += mismatch
      ingap = false
    else:
      if ingap:
        result += gap_extend
      else:
        result += gap_open
        ingap = true


proc repr*(a:Alignment): array[2, string] =
  ## return a representation of the alignment as target, query array.
  #* 0 stands for match.
  #* 1 stands for insertion to target.
  #* 2 stands for insertion to query.
  #* 3 stands for mismatch.
  var
    n = a.c.alignmentLength.int
    arr = cast[ptr CArray[uint8]](a.c.alignment.pointer)
    t = new_string_of_cap(n)
    q = new_string_of_cap(n)

  for i in 0..<n:
    var v = cast[int](arr[i])
    t.add(lookupt[v])
    q.add(lookupq[v])

  return [t, q]

proc `$`*(a:Alignment): string =
  var s = a.repr
  return s[0] & " target\n" & s[1] & " query"

when isMainModule:

  var cfg = new_config()
  var t = "TACTGTCCCCATGCGAGTGAG"
  var q = "AACTGT   CATGCGAGTGaG".replace(" ", "")

  var aln = q.align_to(t, cfg)
  var cigar_s = ""
  assert aln.cigar(cigar_s) == "7M3D11M"
  assert aln.cigar(cigar_s, extended=true) == "1X6=3D11="
  assert aln.score == 12 # 17 matches - 1MM = 16 - 1gap_o == 14 - 2 gap_e == 12

  t = "CCCCCCCCCCCAACTGTCCCCATGCGAGTGAGCCCCCCCCC"
  q = "AACTGTCATGCGAGTGAG"

  aln = q.align_to(t, cfg)
  assert aln.cigar(cigar_s) == "7M3D11M", cigar_s
  assert aln.start == 11
  echo aln.cigar(cigar_s, extended=true)

  t = "AACTGTCCCCATGCGAGTGAG"
  q = "GACTGTCTTTTAGCTAGTGAG"
  cfg = new_config(k=3)
  aln = q.align_to(t, cfg)
  assert (not(aln.ok))
  assert aln.start == -1

  var c = new_config(k=20)
  var tgt = "CCCCCTGCTCATCGAGACCTACGTGGGACTCATGTCCTTCATTAACAACGAGGCGAAACTGGGCTACTCCATGACCAGGGGCAAAATAGGCTTTTAGCCGCTGCGTTCTGGGAGCTCCTCCCCCTTCTGGGAGCTCCTCCCCCTCCCCAGAAGGCCAAGGGATGTGGGGGCTGGGGGACTGGGAGGCCTGGCAGTCTT"
  var qry =                                                      "CGAAACTGGGCTACTCCATGACCAGGGGCAAAATAGGCTTTTAGCCGCTGCGTTCTGGGAGCTCCTCCCCCTCCCCAGAAGGCCAAGGGATGTTGGGG"

  var a = qry.align_to(tgt, c)
  echo a.cigar(cigar_s)
  echo $a

