Copy-number values and exome bams for 1kg.

http://www.nature.com/nature/journal/v464/n7289/extref/nature08516-s4.xls

Given the truth sets in the XLS and the bams from 1KG, we can evaluate a CNV caller by recovery of those from the truth
set.

Go
==

```Go

type interval struct {
    start int
    end int
    sample string
}

type Truthy struct {
    ProportionOverlap float64
    // tree will return an interval for each sample
    tree *IntervalTree
}

func imin(a, b int) int {
    if a < b {
        return a
    }
    return b
}

func imax(a, b int) int {
    if a > b {
        return a
    }
    return b
}

func overlapp(a, b *interval) float64 {
    total := a.end - a.start + b.end - b.start
    // -----
    //   ------
    ovl := imin(a.end, b.end) - imax(a.start, b.start)
    if ovl < 0 { return 0 }
    return (ovl * 2) / total
}

func (t *Truthy) Has(i *interval) bool {
    values := t.tree.Get(i)
    for _, v := range values {
        if v.Sample() == i.Sample(){
            if overlapp(v, i) >= t.ProportionOverlap {
                return true
            }
        }
    }
    return false
}

type Evaluator struct {
    t *Truthy
    FP int
    TP int
    // calculate true and false negatives by tracking what's touched in the tree.
    FN int
    TN int
}

func (e Evaluator) Precision() float64 { }
func (e Evaluator) Recall() float64 { }
func (e *Evaluator) Clear() {
    e.TP, e.FP, e.TN, e.FN = 0, 0, 0, 0
}


func (e *Evaluator) LoadTruth(bedpath string) error { }
func (e *Evaluator) Evaluate(bedpath string) error { }

```

