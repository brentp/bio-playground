import times

const
  FML_VERSION* = "r53"

type
  bseq1_t* {.byref.} = object
    l_seq*: int32
    seq*: cstring
    qual*: cstring             ##  NULL-terminated strings; length expected to match $l_seq
  

const
  MAG_F_AGGRESSIVE* = 0x00000020
  MAG_F_POPOPEN* = 0x00000040
  MAG_F_NO_SIMPL* = 0x00000080

type
  magopt_t* {.byref.} = object
    flag*: cint
    min_ovlp*: cint
    min_elen*: cint
    min_ensr*: cint
    min_insr*: cint
    max_bdist*: cint
    max_bdiff*: cint
    max_bvtx*: cint
    min_merge_len*: cint
    trim_len*: cint
    trim_depth*: cint
    min_dratio1*: cfloat
    max_bcov*: cfloat
    max_bfrac*: cfloat

  fml_opt_t* {.byref.} = object
    n_threads*: cint           ##  number of threads; don't use multi-threading for small data sets
    ec_k*: cint                ##  k-mer length for error correction; 0 for auto estimate
    min_cnt*: cint
    max_cnt*: cint             ##  both occ threshold in ec and tip threshold in cleaning lie in [min_cnt,max_cnt]
    min_asm_ovlp*: cint        ##  min overlap length during assembly
    min_merge_len*: cint       ##  during assembly, don't explicitly merge an overlap if shorter than this value
    mag_opt*: magopt_t         ##  graph cleaning options
  
  rld_t* {.bycopy.} = object
  
  mag_t* {.bycopy.} = object
  
  fml_ovlp_t* {.bycopy.} = object
    len* {.bitsize: 31.}: uint32
    `from`* {.bitsize: 1.}: uint32 ##  $from and $to: 0 meaning overlapping 5'-end; 1 overlapping 3'-end
    id* {.bitsize: 31.}: uint32
    to* {.bitsize: 1.}: uint32 ##  $id: unitig number
  
  fml_utg_t* {.byref.} = object
    len*: int32              ##  length of sequence
    nsr*: int32              ##  number of supporting reads
    seq*: cstring              ##  unitig sequence
    cov*: cstring              ##  cov[i]-33 gives per-base coverage at i
    n_ovlp*: array[2, cint]     ##  number of 5'-end [0] and 3'-end [1] overlaps
    ovlp*: ptr fml_ovlp_t       ##  overlaps, of size n_ovlp[0]+n_ovlp[1]
  

var fm_verbose*: cint

## ***********************
##  High-level functions *
## **********************
## *
##  Read all sequences from a FASTA/FASTQ file
## 
##  @param fn       filename; NULL or "-" for stdin
##  @param n        (out) number of sequences read into RAM
## 
##  @return array of sequences
## 

proc fml_opt_init*(opt: ptr fml_opt_t) {.cdecl,  importc: "fml_opt_init".}
## *
##  Assemble a list of sequences
## 
##  @param opt      parameters
##  @param n_seqs   number of input sequences
##  @param seqs     sequences to assemble; FREED on return
##  @param n_utg    (out) number of unitigs in return
## 
##  @return array of unitigs
## 

proc fml_assemble*(opt: ptr fml_opt_t; n_seqs: cint; seqs: ptr bseq1_t; n_utg: ptr cint): ptr fml_utg_t {.
    cdecl, importc: "fml_assemble" .}
## *
##  Free unitigs
## 
##  @param n_utg    number of unitigs
##  @param utg      array of unitigs
## 

proc fml_utg_destroy*(n_utg: cint; utg: ptr fml_utg_t) {.cdecl, importc: "fml_utg_destroy"}
## ***********************************************
##  Mid-level functions called by fml_assemble() *
## **********************************************
## *
##  Adjust parameters based on input sequences
## 
##  @param opt       parameters to update IN PLACE
##  @param n_seqs    number of sequences
##  @param seqs      array of sequences
## 

proc fml_opt_adjust*(opt: ptr fml_opt_t; n_seqs: cint; seqs: ptr bseq1_t) {.cdecl, importc: "fml_opt_adjust"}
## *
##  Error correction
## 
##  @param opt       parameters
##  @param n         number of sequences
##  @param seq       array of sequences; corrected IN PLACE
## 
##  @return k-mer coverage
## 

proc fml_correct*(opt: ptr fml_opt_t; n: cint; seq: ptr bseq1_t): cfloat {.cdecl, importc: "fml_correct"}
proc fml_fltuniq*(opt: ptr fml_opt_t; n: cint; seq: ptr bseq1_t): cfloat {.cdecl, importc: "fml_fltuniq"}
## *
##  Construct FMD-index
## 
##  @param opt       parameters
##  @param n         number of sequences
##  @param seq       array of sequences; FREED on return
## 
##  @return FMD-index
## 

proc fml_seq2fmi*(opt: ptr fml_opt_t; n: cint; seq: ptr bseq1_t): ptr rld_t {.cdecl, importc: "fml_seq2fmi"}
## *
##  Generate initial overlap graph
## 
##  @param opt       parameters
##  @param e         FMD-index; FREED on return
## 
##  @return overlap graph in the "mag" structure
## 

proc fml_fmi2mag*(opt: ptr fml_opt_t; e: ptr rld_t): ptr mag_t {.cdecl, importc: "fml_fmi2mag"}
## *
##  Clean a mag graph
## 
##  @param opt       parameters
##  @param g         overlap graph; modified IN PLACE
## 

proc fml_mag_clean*(opt: ptr fml_opt_t; g: ptr mag_t) {.cdecl, importc: "fml_mag_clean"}
## *
##  Convert a graph in mag to fml_utg_t
## 
##  @param g         graph in the "mag" structure; FREED on return
##  @param n_utg     (out) number of unitigs
## 
##  @return array of unitigs
## 

proc fml_mag2utg*(g: ptr mag_t; n_utg: ptr cint): ptr fml_utg_t {.cdecl, importc: "fml_mag2utg"}
## *
##  Output unitig graph in the mag format
## 
##  @param n_utg     number of unitigs
##  @param utg       array of unitigs
## 

proc fml_utg_print*(n_utgs: cint; utg: ptr fml_utg_t) {.cdecl, importc: "fml_utg_print"}
## *
##  Output unitig graph in the GFA format
## 
##  @param n_utg     number of unitigs
##  @param utg       array of unitigs
## 

proc fml_utg_print_gfa*(n: cint; utg: ptr fml_utg_t) {.cdecl, importc: "fml_utg_print_gfa"}
## *
##  Deallocate an FM-index
## 
##  @param e         pointer to the FM-index
## 

proc fml_fmi_destroy*(e: ptr rld_t) {.cdecl, importc: "fml_fmi_destroy"}
## *
##  Deallocate a mag graph
## 
##  @param g         pointer to the mag graph
## 

proc fml_mag_destroy*(g: ptr mag_t) {.cdecl, importc: "fml_mag_destroy"}

proc bseq_read*(p: cstring, nseqs: ptr cint): ptr bseq1_t {.cdecl, importc:"bseq_read".}

template ptrMath*(body: untyped) =
  template `+`*[T](p: ptr T, off: int): ptr T =
    cast[ptr type(p[])](cast[ByteAddress](p) +% off * sizeof(p[]))

  template `+=`*[T](p: ptr T, off: int) =
    p = p + off

  template `-`*[T](p: ptr T, off: int): ptr T =
    cast[ptr type(p[])](cast[ByteAddress](p) -% off * sizeof(p[]))

  template `-=`*[T](p: ptr T, off: int) =
    p = p - off

  template `[]`*[T](p: ptr T, off: int): T =
    (p + off)[]

  template `[]=`*[T](p: ptr T, off: int, val: T) =
    (p + off)[] = val

  body

type CArray*{.unchecked.}[T] = array[0..0, T]
type CPtr*[T] = ptr CArray[T]

type SafeCPtr*[T] =
  object
    size: int
    mem: CPtr[T]

proc safe*[T](p: CPtr[T], k: int): SafeCPtr[T] =
   SafeCPtr[T](mem: p, size: k)

proc len*[T](p:  SafeCPtr[T]): int =
  return p.size

proc safe*[T](a: var openarray[T], k: int): SafeCPtr[T] =
  safe(cast[CPtr[T]](addr(a)), k)

proc `[]`*[T](p: SafeCPtr[T], k: int): T =
  when not defined(release):
    assert k < p.size
  result = p.mem[k]

proc `[]=`*[T](p: SafeCPtr[T], k: int, val: T) =
  when not defined(release):
    assert k < p.size
  p.mem[k] = val

type Fermi* = ref object of RootObj
  ## Fermi wraps the parts we need from fermikit
  seqs: seq[bseq1_t]
  opt: fml_opt_t

type Tigs* = ref object of RootObj
  utgs: ptr fml_utg_t
  n :   cint
  s : SafeCPtr[fml_utg_t]

proc `[]`*(t: Tigs, k: int): fml_utg_t =
  return t.s[k]

proc len*(t: Tigs): int =
  return t.n.int

iterator items*(t: Tigs): fml_utg_t =
  for i in 0..<t.n.int:
    yield t[i]

proc destroy_tig(t:Tigs) =
  if t.n != 0:
    fml_utg_destroy(t.n, t.utgs)
    t.n = 0

proc new_fermi*(): Fermi =
  ## create a new Fermi with default options
  var opt = fml_opt_t()
  fml_opt_init(opt.addr)
  #opt.min_asm_ovlp = 29
  opt.mag_opt.flag = opt.mag_opt.flag or MAG_F_AGGRESSIVE
  return Fermi(seqs: new_seq[bseq1_t](),
               opt: opt)
   
proc add*(f: Fermi, dna_seq: string, qual: string=nil) {.inline.}=
  var cpy = dna_seq
  GC_unref(cpy)
  var b = bseq1_t(seq: cstring(cpy), l_seq: dna_seq.len.cint)
  if qual != nil:
    var cpy2 = qual
    GC_unref(cpy2)
    b.qual = cpy2
  f.seqs.add(b)

proc assemble*(f: Fermi): Tigs =
  ## assemble the sequences and return an array-like of unitigs.
  var t: Tigs
  if len(f.seqs) == 0:
    return t

  new(t, destroy_tig)

  #for s in f.seqs:
    #GC_unref(s.seq)
    #GC_unref(s.qual)

  var ti = cpuTime()
  t.utgs = fml_assemble(f.opt.addr, f.seqs.len.cint, f.seqs[0].addr, t.n.addr)
  f.seqs = new_seq[bseq1_t]() # release mem from existing
  t.s = safe(cast[CPtr[fml_utg_t]](t.utgs), t.n.int)
  return t

when isMainModule:
  var dna = "AAAAACTCTACCTCTCTATACTAATCTCCCTACAAATCTCCTTAATTATAACATTCACAGCCACAGAACTAATCATATTTTATATCTTCTTCGAAACCAC"
  var qual = "2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222"

  for k in 0..100:

    var fml = new_fermi()
    var i = 0
    while i <= (dna.len - 80 + 3):
      var s = dna[i..<(i+80)]
      var q = qual[0..<s.len]
      fml.add(s, q)
      i += 3

    var tigs = fml.assemble()
    echo dna
    echo tigs[0].seq
    echo len(tigs)

    for t in tigs:
      echo t.seq
      echo t.len
