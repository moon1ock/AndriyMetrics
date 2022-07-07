
<h1 align="center">
  MAG Depth Uniqueness & Interdisciplinarity
</h1>

## Table of Contents 

- 


## Overview 

In this repository you can find the algorithm for the _Depth_ _Uniqueness_ & _Interdisciplinarity_ metrics calculation for _Microsoft Academic Graph_ _(MAG)_.


## Files

You will need these files from the MAG for the calculation.

- `46G	PaperFieldsOfStudy.txt`

- `71G	Papers.txt`

- `59M	FieldsOfStudy.txt`

- `18M	FieldOfStudyChildren.txt`

## Metrics

We are dealing with the following metrics:

### 1. Uniqueness

The metric is a tuple: `(new_field_2combinations, field_count)`. The `field_count` is how many fields in total this paper has. The `new_field_2combinations` is a counter of how many _unique_ _2-pairs_ of fields this paper introduces comparing to all the papers that were published up to the field's piublication year.

This way the first combination of `feild1+field2` will increment the `new_field_2combinations` value. If a paper has 5 fileds `{f1,f2,f3,f4,f5}`, it's the first time `f5` is introduced and the other 4 fields had been published together, the value of `new_field_2combinations` would be _nCr(5,2)_. In other case, for instance, if all fields except for `field2` and `field5` had appeared together, the value of `new_field_2combinations` would be _1_ because it only introduces _1_ new unseen combination.

> P.S. We cannot interpret “counter” as “innovation” or “novelty”. This is because one may argue that p can be innovative or novel compared to other papers that preceded it, even if all of them had the same vector as p and were published before p (e.g., if p is novel in the way it solved a particular problem, rather than being novel in the topics it studies). In contrast, interpreting “counter” as “uniqueness” is harder to argue against.

### 2. Interdisciplinarity: 

Measure interdisciplinarity in a way similar to lexicographic ordering. 

In MAG there are 6 levels of fields: 19 parent fields (Math, Physics, Biology, etc.), 100+ first children (AI, Astronomy, ML, etc), and so on. We can find the vector of counts of field levels per paper `v = [l0,l1,l2,l3,l4,l5]`.

* The most interdisciplinary papers are those whose 1st value in vector is greatest.

** Out of those, the most interdisciplinary are those whose 2nd value is greatest

** Out of those, the most interdisciplinary are those whose 3rd value is greatest

** And so on…
    
    
Then, we have those whose 2nd value in vector is greatest. 
Out of those, the most interdisciplinary are those whose 3rd value is greatest
Out of those, the most interdisciplinary are those whose 4th value is greatest
And so on…

### 3. Depth: This is simply x.

P.S., it seems intuitive to interpret “x” as “depth”


