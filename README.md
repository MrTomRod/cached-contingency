# CachedContingency

Python 3.9+ classes to compute and cache
[Fisher's exact test](https://en.wikipedia.org/wiki/Fisher%27s_exact_test) and
[Boschloo's test](https://en.wikipedia.org/wiki/Boschloo%27s_test) more efficiently.

## Installation

This package requires at least `Python 3.9`.

```bash
pip install cached_contingency
```

## Idea

I have to compute lots of these tests and want to accelerate the process. There are two optimizations that came to my mind:

1) My contingency tables often have identical column sums, so many tests can be recycled
2) Some contingency tables are equivalent and only have to be computed once
    * Fisher's test: `abcd`, `acbd`, `badc`, `bdac`, `cadb`, `cdab`, `dbca` and `dcba` are equivalent (pvalue, _not_ odds ratio)
    * Boschloo's test: `abcd`, `badc`, `cdab` and `dcba` are equivalent

Furthermore, sometimes, one has to re-run tools. In these cases, all previously computed results can be recycled.

As cache, an SQLite database is used.

### Execution

1) Replace equivalent contingency tables with the same contingency table
2) Find all tests that are not cached yet
3) Calculate them in parallel, using all CPU cores
4) Add them to the cache
5) Return results

## Usage

Set the location of the cache database:

```bash
export KEY_VALUE_STORE_DB=/custom/path.db  # default: ~/.cache/keyvaluestore.db
```

Calculate single tests:

```python
from cached_contingency import CachedFisher, CachedBoschloo, odds_ratio
from scipy.stats import fisher_exact, boschloo_exact
from numpy import isclose

# Create class (automatically creates database if none exists yet)
cf = CachedFisher()
# Calculate Fisher's test
pval_cache = cf.get_or_create(74, 31, 43, 32)
odds_ratio_cache = odds_ratio(74, 31, 43, 32)
# This is equivalent to:
odds_ratio_calc, pval_calc = fisher_exact([[74, 31], [43, 32]])
assert isclose(pval_cache, pval_calc)
assert isclose(odds_ratio_cache, odds_ratio_calc)

# Create class (automatically creates database if none exists yet)
cb = CachedBoschloo()
# Calculate Fisher's test
pval_cache = cb.get_or_create(74, 31, 43, 32)
# This is almost* equivalent to:
pval_calc = boschloo_exact([[74, 31], [43, 32]]).pvalue
assert isclose(pval_cache, pval_calc)
```

* \*: Not exactly equivalent: My function never returns pvalues greater than 1 and never returns nan as pvalues.
  (See [scipy issue](https://github.com/scipy/scipy/issues/15345).)

Calculate multiple tests:

```python
from cached_contingency import CachedFisher, CachedBoschloo
import pandas as pd
import numpy as np

# Create class (automatically creates database if none exists yet)
cb = CachedBoschloo()

# Create test DataFrame, column names are important!
np.random.seed(42)
test_df = pd.DataFrame(
    [(np.random.randint(200) for _ in range(4)) for _ in range(5)],
    columns=['c1r1', 'c2r1', 'c1r2', 'c2r2']
)
print(test_df)
#    c1r1  c2r1  c1r2  c2r2
# 0   102   179    92    14
# 1   106    71   188    20
# 2   102   121    74    87
# 3   116    99   103   151
# 4   130   149    52     1

# Calculate multiple Boschloo's tests
result_df = cb.get_or_create_many(test_df)
print(result_df)
#    c1r1  c2r1  c1r2  c2r2          pval   fisher_stat
# 0   102   179    92    14  3.442564e-20  3.974758e-20
# 1   106    71   188    20  1.144156e-12  1.197655e-12
# 2   102   121    74    87  9.692791e-01  5.239450e-01
# 3   116    99   103   151  3.821222e-03  2.490365e-03
# 4   130   149    52     1  1.831830e-14  1.595989e-14

# If you run this again, the results will be loaded from cache:
result_df = cb.get_or_create_many(test_df)
print('Like a flash!')
```

**Advanced usage:**

Alternative way to specify the path to the database via Python and change number of CPUs:

```python
from cached_contingency import CachedFisher

cf = CachedFisher(db_path='/custom/path.db', n_cpus=1)
```
