
<h1 align="center">
  MAG Depth Uniqueness & Interdisciplinarity
</h1>

## Table of Contents

- [Overview](#overview)
- [Files](#files)
- [Metrics](#metrics)
  * [1. Uniqueness](#1-uniqueness)
  * [2. Interdisciplinarity](#2-interdisciplinarity)
  * [3. Depth](#3-depth)
- [Algorithm](#algorithm)
- [Data Sample](#data-sample)
- [Usage](#usage)


## Overview 

In this repository you can find the algorithm for the _Depth_ _Uniqueness_ & _Interdisciplinarity_ metrics calculation for _Microsoft Academic Graph_ _(MAG)_.

The metrics are calculated at `26GB /scratch/aal544/AndriyMetrics/AndriyMetrics.csv`. The table includes the metrics for _152M_ papers. `bka3` has root permissions to the directory / file. Expect the code re-runs to run _10-12 hours_.



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

### 2. Interdisciplinarity

Measure interdisciplinarity in a way similar to lexicographic ordering. 

In MAG there are 6 levels of fields: 19 parent fields (Math, Physics, Biology, etc.), 100+ first children (AI, Astronomy, ML, etc), and so on. We can find the vector of counts of field levels per paper `v = [l0,l1,l2,l3,l4,l5]`.

- The most interdisciplinary papers are those whose 1st value in vector is greatest.

    - Out of those, the most interdisciplinary are those whose 2nd value is greatest

    - Out of those, the most interdisciplinary are those whose 3rd value is greatest

    - And so on…
    
    
- Then, we have those whose 2nd value in vector is greatest. 

    - Out of those, the most interdisciplinary are those whose 3rd value is greatest

    - Out of those, the most interdisciplinary are those whose 4th value is greatest

    - And so on…


### 3. Depth

This is the index of the last non-zero value in the counts of field levels per paper `v = [l0,l1,l2,l3,l4,l5]` vector. 

Since the field levels are hierarchical in MAG, the lower the field is — the more specific in relation to the science it is.


## Algorithm

The code for computing the metrics is available here in the repository. It is well commented and segmented.

Synopsis:

1. `Global Vars`
    - `ENV` can be set to `test` or `HPC` for local and production execution.
    - `FIELD_CONFIDENCE` is the threshold for the MAG certainty of the field per paper. It is _>50%_ by default.
    
2. `Paths`
    - Set the path to the parent folder of MAG (it will be the place where data is saved)
    - Set the name of the MAG folder

3. `Get the Paper-Field associations`
    - Group papers and paper fields by _PID_
    - Drop all fields that are below the threshold of certainty

4. `Get the Paper Publication Years`
    - Merge each paper with its publication year

5. `Extend Fields with the Parent Fields` 
    - Run _BFS_ on fields that we have to propagate up and note all parent fields. For instance, if _Eigen Decomposition_ is a field we add its parent _Linear Algebra_ and its parent _Math_ to the fields of the paper.

6. `Count Fields per Level`
    - Calculate the `v` vector of field counts per level per paper.

7. `Calculate Uniqueness`
    - Run a linear scan and update the tuple counts every year.
    - For every field set per paper, find all the `2 combinations` of the fields and keep track of which ones appear for the first time.

8. `Get Depth and Interdisciplinarity`
    - Convert the `v` vector into a scaled value, and standardize the distribution to keep it in bounds.
    - Save the index of the last non-zero value of the `v` vector.

9. `Save the Metrics`
    - save the file to `path`


## Data Sample

|PID      |PaperFields                                                                                         |PubYear|LevelCounts       |New_Tuples|Field_Count|Depth|Interdisciplinarity|
|---------|----------------------------------------------------------------------------------------------------|-------|------------------|----------|-----------|-----|-------------------|
|3483532  |{199539241, 190136086, 111472728, 17744445, 138885662}                                              |1825   |[2, 2, 1, 0, 0, 0]|10        |5          |2    |-0.6337096715235878|
|152588939|{71924100, 141071460, 2780401607, 86803240, 151730666, 127313418, 105702510, 2780193326, 2779777117}|1884   |[3, 3, 2, 1, 0, 0]|36        |9          |3    |0.05073388992405839|
|134480136|{111472728, 2780349523, 138885662}                                                                  |1893   |[1, 1, 1, 0, 0, 0]|2         |3          |2    |-1.3179426349523269|
|76015792 |{71924100, 2778536324, 141071460, 86803240, 2778722699, 105702510}                                  |1904   |[2, 2, 2, 0, 0, 0]|9         |6          |2    |-0.6335027045050068|
|118077477|{54355233, 24107716, 185592680, 86803240, 55493867}                                                 |1906   |[2, 2, 1, 0, 0, 0]|10        |5          |2    |-0.6337096715235878|
|173670722|{2780550144, 50522688, 199539241, 162324750, 17744445}                                              |1914   |[2, 2, 1, 0, 0, 0]|9         |5          |2    |-0.6337096715235878|
|114636826|{185592680, 178790620, 2777517455}                                                                  |1918   |[1, 1, 1, 0, 0, 0]|3         |3          |2    |-1.3179426349523269|
|58810875 |{2524010, 2781425163, 33923547}                                                                     |1919   |[1, 1, 1, 0, 0, 0]|3         |3          |2    |-1.3179426349523269|


## Usage

If you intend on using the `PaperFields` set, use `{'PaperFields':literal_eval}`, but it is **slow**. Otherwise, just read it in as a string.

```python3
pd.read_csv(path + filename, usecols=['PID','PaperFields', 'PubYear'], converters={'PaperFields':literal_eval})
```




