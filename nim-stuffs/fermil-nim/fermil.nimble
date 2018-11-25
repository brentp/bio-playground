# Package

version       = "0.2.0"
author        = "Brent Pedersen"
description   = "fermi-list wrapper to assemble short reads"
license       = "MIT"

# Dependencies

requires "nim >= 0.17.2" #, "nim-lang/c2nim>=0.9.13"

task test, "run the tests":
  exec "make"
  exec "nim c -d:release --threads:on --passL:libfml.a --passL:-lz -r fermil.nim"

task build, "build":
  exec "make"
  exec "nim c --threads:on --passL:libfml.a --passL:-lz -r fermil.nim"

before install:
  exec "make"
