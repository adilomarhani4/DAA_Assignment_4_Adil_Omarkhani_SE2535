# Assignment 4 — analysis

## Environment and commands

- Selected language: **Python 3.12+** (tested with Python 3.13.5).
- Runtime: CPython 3.13.5, Linux x86_64 container. The environment exposed 5 logical CPUs and approximately 5.8 GiB RAM; the exact CPU model was not exposed.
- No third-party packages are required.
- Setup: `python tools/run.py --setup`
- Own tests: `python -m unittest discover -s tests/student -v`
- Public input/output protocol: `python tools/run.py --input examples/lcs.jsonl`
- Public checker: `python tools/run.py --check`

The setup command passed (`PASS setup: ping`). The seven student test methods passed. I also sent all 44 supplied public requests twice through one persistent process (88 requests total) and validated every answer with the template's `tools/public_validate.py`: 88 answers, 0 failures. This checks both public cases and mixed-request state reset. The full launcher `--check` was not completed in this execution environment because its many separate Python process launches exceeded the environment's 60-second execution window; it should be rerun locally before submission.

## Algorithm explanations

### 1. LCS — `lcs`

`dp[i][j]` is the length of a longest common subsequence of prefixes `a[:i]` and `b[:j]`. Row zero and column zero are zero because an empty string has no nonempty common subsequence. If the last characters are equal, the optimum is `dp[i-1][j-1] + 1`. Otherwise, the optimum is the larger of dropping the last character of `a` or dropping the last character of `b`: `max(dp[i-1][j], dp[i][j-1])`. Rows are filled in increasing `i`, and columns in increasing `j`, so both dependencies are already available.

Reconstruction starts at `(n,m)`. Equal final characters are included and both indices move diagonally. On a mismatch, move to the neighbour with the same DP value; ties may choose either direction. This follows an optimal predecessor at every step. Reversing the collected characters gives a subsequence of both inputs with length `dp[n][m]`. Time and auxiliary memory are `O((n+1)(m+1))`.

Boundary check: `a=""`, `b="abc"` must return length zero and an empty witness. `tea_time` versus `team` checks subsequence rather than substring semantics.

### 2. Ordered adjacent merging — `merge`

`dp[l][r]` is the minimum cost to merge the original contiguous interval `[l,r]` into one block. A one-element interval costs zero. If the final merge splits the interval after `k`, the two already-merged children cost `dp[l][k] + dp[k+1][r]`; the final merge costs the sum of all original sizes in `[l,r]`. Therefore the transition minimizes that expression over `l <= k < r`. Prefix sums calculate each interval sum in constant time.

Intervals are processed by increasing width, so all shorter child intervals are ready. `split[l][r]` stores an optimal final split. An explicit postorder stack emits the left and right child plans before `[l,k,r]`; this is chronological and always merges adjacent blocks. The time and auxiliary memory are `O(n^3)` and `O(n^2)`. The empty and one-block cases return cost zero and no operations.

Boundary check: `[2,3,4]` has optimum 14. Merging the non-adjacent smallest and largest blocks is not allowed; this detects an invalid greedy solution.

### 3. Tree maximum-weight independent set — `tree`

The tree is rooted at vertex zero using an iterative traversal. `take[u]` is the best weight in the subtree when `u` is selected; `skip[u]` is the best when it is not selected. For each child `v`, selecting `u` forces `v` to be skipped, so `take[u] = weight[u] + sum(skip[v])`. If `u` is skipped, each child independently contributes `max(take[v],skip[v])`. The traversal order is reversed for the DP, which is a postorder because parents are added before descendants in the forward order.

Reconstruction uses a stack carrying whether the parent was selected. A vertex is selected only if its parent was not selected and `take[u] > skip[u]`; ties choose skip, which remains optimal. The empty set is allowed, so negative weights never force a selection. Iterative traversal and reconstruction avoid recursion-depth failure on a chain. Time and auxiliary memory are `O(n)`.

Boundary checks: all-negative weights return weight zero and an empty set. A 20,000-vertex chain checks deep-tree safety and adjacency validity; a 100,000-vertex chain was also exercised as a scale check.

### 4. Exact single-pattern search — `naive`, `kmp`, `rk`

All three return every zero-based match start in increasing order, including overlaps. An empty pattern matches all `n+1` text boundaries; a pattern longer than the text has no matches.

- **Naive:** test each start from zero through `n-m`, comparing characters left to right until mismatch or a complete match. It uses `O(1)` auxiliary memory and `O(n*m+n+1)` time including output.
- **KMP:** the prefix function `pi[i]` is the length of the longest proper prefix of `pattern[:i+1]` that is also its suffix. On mismatch, set the matched-prefix length to `pi[j-1]` rather than restarting. After a full match, the same fallback retains possible overlapping matches. Prefix construction and scanning take `O(n+m+z)` time; auxiliary memory is `O(m)`, plus `O(z)` output.
- **Rabin–Karp:** the polynomial hash uses base 31 and modulus 101, with ASCII character codes and the leftmost character at the highest power. The next window hash removes the outgoing character's weighted contribution, multiplies by the base and adds the incoming character. Python's `%` normalizes the result to a nonnegative residue. A hash match is only a candidate: every character is compared before reporting it. If `c` windows have the pattern hash, time is `O(n+m+c*m)`; worst case can be quadratic. Auxiliary memory is `O(m)` plus output.

Boundary checks cover empty text, empty pattern, longer pattern, punctuation/case, overlaps and the deliberate collision `text="abdj", pattern="ab"`: `ab` and `dj` have the same hash under this tiny modulus, but only start zero is returned. A seeded 300-case randomized comparison checks KMP and RK against the independent naive baseline.

### 5. Suffix array and Kasai LCP — `suffix`

Prefix doubling starts with each character's ASCII rank. At doubling length `k`, each suffix is sorted by the pair `(rank[i], rank[i+k])`, using `-1` when the second half is past the end. New equivalence-class ranks are assigned from the sorted pairs. The length doubles until every suffix has a distinct rank. The implementation sorts rank pairs directly, giving `O(n log^2(n+1))` time and `O(n)` auxiliary memory; it does not construct suffix strings or append a sentinel to the output.

Kasai builds the inverse suffix-array position. For each text start `i`, it compares its suffix with the previous suffix in suffix-array order. The previous LCP value is reused with one character removed, so total comparison work is linear. `lcp[0]` is zero. The maximum LCP of adjacent suffixes is the longest repeated substring: if any two suffixes share a prefix, the suffixes between them in lexicographic order have an adjacent pair sharing at least that prefix. The substring is taken from one suffix at an index attaining the maximum. Time is `O(n log^2(n+1))` overall and memory is `O(n)`.

Boundary checks include empty text, one character, all-equal, all-distinct and overlapping repeats (`banana` gives `ana`). The scale check uses 50,000 characters.

### 6. Aho–Corasick — `aho`

A trie stores each distinct prefix as a state. Terminal states store the original dictionary indices, so duplicate pattern strings remain separate output columns. Breadth-first construction assigns failure links: a child transition follows the longest proper suffix that is also a trie prefix. During text scanning, mismatch follows failure links until a transition exists or the root is reached.

For each independent text, the automaton state resets to root and a visit counter is incremented at the reached state. After scanning, states are processed in reverse BFS order, adding each state's visits to its failure parent. Thus every visit contributes to all terminal suffix-pattern states without enumerating every match. Terminal visit totals are copied to all duplicate dictionary positions. This counts overlaps and suffix patterns efficiently. With a fixed ASCII alphabet of 95 printable characters, construction is `O(L+95*S+p)` as specified; scanning and reverse propagation per text are `O(|text|+S+p)`. Auxiliary memory is `O(95*S+p)` and output memory follows the number of texts and patterns.

Boundary checks include no patterns, no texts, empty text, duplicate patterns, suffix patterns (`he` in `she`) and repeated independent texts. The example returns `[2,2,2]` for each `sheshe` text and zeros for the empty text.

## Own tests

Run: `python -m unittest discover -s tests/student -v`

| Test / fixture | Expected result | Actual result | What it checks |
|---|---|---|---|
| `test_lcs` | length 4 for `tea_time` / `team`; empty witness for empty input | PASS | subsequence witness and empty boundary |
| `test_merge_and_plan` | cost 14, two chronological merges | PASS | optimal cost, adjacent interval availability, empty input |
| `test_tree` | optimum 10; all-negative optimum 0; 20,000-chain optimum 10,000 | PASS | independent-set witness, empty-set option, deep chain |
| `test_searches` | naive/KMP/RK return identical starts for all fixed cases | PASS | empty pattern, overlaps, collision, case, longer pattern |
| `test_suffix` | suffix order and LCP valid for seven short strings | PASS | empty, repeated, distinct and overlapping text |
| `test_aho` | counts `[[2,2,2],[2,2,2],[0,0,0]]` for the published example | PASS | suffix patterns, duplicates, reset, empty dictionary |
| `test_random_search_equivalence` | 300 seeded cases agree with naive | PASS | independent cross-check of KMP and RK |

Additional scale run completed in approximately 1.93 seconds in this environment: LCS with two 1,000-character strings; merge with 200 blocks of size one billion; a 100,000-vertex tree chain; KMP on 200,000 text characters and a 100,000-character pattern; RK on a 10,000-character text and 2,000-character pattern; suffix array on 50,000 characters; and Aho–Corasick with 10,000 patterns and long texts. Results had the expected output dimensions and values.

## Search comparison

All three implementations were run on identical inputs. Generator: `random.Random(20261108)`; random text characters were selected uniformly from lowercase ASCII letters, and the pattern was a length-`m` slice starting at `n//2`. The repetitive case used text `"a"*n` and pattern `"a"*m`. Sizes were `(n,m) = (300,30), (900,90), (1800,180)`. Each function was warmed once, then timed three times with `time.perf_counter`; the timed scope was the function call including output-list creation. Compilation and JSON transport were excluded. CPython has no JIT. All three outputs were compared before timing and every timed result was checked against the naive output. Times are milliseconds; medians are shown.

| Case | n | m | Algorithm | Run 1 | Run 2 | Run 3 | Median | Matches |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| random | 300 | 30 | naive | 0.0166 | 0.0167 | 0.0169 | 0.0167 | 1 |
| random | 300 | 30 | KMP | 0.0146 | 0.0139 | 0.0137 | 0.0139 | 1 |
| random | 300 | 30 | RK | 0.0466 | 0.0457 | 0.0453 | 0.0457 | 1 |
| random | 900 | 90 | naive | 0.0536 | 0.0709 | 0.0555 | 0.0555 | 1 |
| random | 900 | 90 | KMP | 0.0440 | 0.0443 | 0.0437 | 0.0440 | 1 |
| random | 900 | 90 | RK | 0.1456 | 0.1450 | 0.1566 | 0.1456 | 1 |
| random | 1800 | 180 | naive | 0.1111 | 0.1257 | 0.1576 | 0.1257 | 1 |
| random | 1800 | 180 | KMP | 0.0902 | 0.1460 | 0.0910 | 0.0910 | 1 |
| random | 1800 | 180 | RK | 0.2944 | 0.3257 | 0.4744 | 0.3257 | 1 |
| repetitive | 300 | 30 | naive | 0.4039 | 0.5321 | 0.3624 | 0.4039 | 271 |
| repetitive | 300 | 30 | KMP | 0.0295 | 0.0292 | 0.0292 | 0.0292 | 271 |
| repetitive | 300 | 30 | RK | 0.2899 | 0.2694 | 0.2701 | 0.2701 | 271 |
| repetitive | 900 | 90 | naive | 3.9072 | 3.4734 | 3.2947 | 3.4734 | 811 |
| repetitive | 900 | 90 | KMP | 0.1209 | 0.1028 | 0.1020 | 0.1028 | 811 |
| repetitive | 900 | 90 | RK | 3.3410 | 2.5012 | 2.7728 | 2.7728 | 811 |
| repetitive | 1800 | 180 | naive | 12.8539 | 14.0254 | 13.1222 | 13.1222 | 1621 |
| repetitive | 1800 | 180 | KMP | 0.2258 | 0.2099 | 0.2088 | 0.2099 | 1621 |
| repetitive | 1800 | 180 | RK | 9.8954 | 9.5643 | 9.8563 | 9.8563 | 1621 |

The repetitive case exposes the difference between the algorithms: naive repeatedly compares long matching prefixes, while KMP reuses prefix information. RK also verifies many equal-hash windows; with base 31 and modulus 101, the small modulus increases collisions and candidate verification work. The random measurements are very small and show noticeable timing noise, so they should not be interpreted as an asymptotic proof or a universal speed ranking. The deliberately small modulus is a correctness teaching device, not representative of every production hash configuration.

## AI Usage and Acknowledgements

- The official Assignment 4 template, README, and instructor's requirements were used to complete the assignment.
- ChatGPT was used to clarify requirements, assist with algorithm development and review, create tests, and explain time and space complexity.
- I am responsible for reviewing the code, understanding each algorithm, and ensuring the final project is ready for submission.