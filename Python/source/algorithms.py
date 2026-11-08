"""Reference implementations for Assignment 4 algorithms.

All functions accept one JSON request dictionary and return a JSON-serializable
dictionary. No algorithm relies on a built-in substring-search routine.
"""

def lcs(request):
    a, b = request["a"], request["b"]
    n, m = len(a), len(b)
    # dp[i][j] is the LCS length of a[:i] and b[:j].
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        row, prev = dp[i], dp[i - 1]
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                row[j] = max(prev[j], row[j - 1])
    # Reconstruct one optimal witness, walking from the final state.
    i, j = n, m
    out = []
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return {"length": dp[n][m], "sequence": "".join(out)}


def merge(request):
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}
    prefix = [0] * (n + 1)
    for i, value in enumerate(sizes):
        prefix[i + 1] = prefix[i] + value
    # dp[l][r] is the minimum cost to merge interval [l,r].
    dp = [[0] * n for _ in range(n)]
    split = [[-1] * n for _ in range(n)]
    for width in range(2, n + 1):
        for left in range(n - width + 1):
            right = left + width - 1
            interval_sum = prefix[right + 1] - prefix[left]
            best = None
            best_k = -1
            for k in range(left, right):
                candidate = dp[left][k] + dp[k + 1][right] + interval_sum
                if best is None or candidate < best:
                    best, best_k = candidate, k
            dp[left][right] = best
            split[left][right] = best_k
    # Postorder traversal emits child merges before their parent.
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        left, right, visited = stack.pop()
        if left == right:
            continue
        if visited:
            plan.append([left, split[left][right], right])
        else:
            k = split[left][right]
            stack.append((left, right, True))
            stack.append((k + 1, right, False))
            stack.append((left, k, False))
    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    n = request["n"]
    if n == 0:
        return {"weight": 0, "selected": []}
    weights = request["weights"]
    graph = [[] for _ in range(n)]
    for u, v in request["edges"]:
        graph[u].append(v)
        graph[v].append(u)

    # Iterative rooting avoids recursion-depth failure on a long chain.
    parent = [-1] * n
    order = [0]
    parent[0] = 0
    for u in order:
        for v in graph[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)

    take = [0] * n
    skip = [0] * n
    for u in reversed(order):
        take_u = weights[u]
        skip_u = 0
        for v in graph[u]:
            if parent[v] == u:
                take_u += skip[v]
                skip_u += max(take[v], skip[v])
        take[u], skip[u] = take_u, skip_u

    optimum = max(take[0], skip[0])
    selected = []
    # If parent is selected, child must be skipped. Otherwise choose best.
    stack = [(0, False)]
    while stack:
        u, parent_taken = stack.pop()
        choose = (not parent_taken) and (take[u] > skip[u])
        if choose:
            selected.append(u)
        for v in graph[u]:
            if parent[v] == u:
                stack.append((v, choose))
    return {"weight": optimum, "selected": selected}


def naive(request):
    text, pattern = request["text"], request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    positions = []
    for start in range(n - m + 1):
        j = 0
        while j < m and text[start + j] == pattern[j]:
            j += 1
        if j == m:
            positions.append(start)
    return {"positions": positions}


def _prefix_function(pattern):
    m = len(pattern)
    pi = [0] * m
    j = 0
    for i in range(1, m):
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    return pi


def kmp(request):
    text, pattern = request["text"], request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    pi = _prefix_function(pattern)
    positions = []
    j = 0
    for i in range(n):
        while j and text[i] != pattern[j]:
            j = pi[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = pi[j - 1]  # retain overlaps
    return {"positions": positions}


def rk(request):
    text, pattern = request["text"], request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    base, mod = 31, 101
    high = pow(base, m - 1, mod)
    pattern_hash = 0
    window_hash = 0
    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        window_hash = (window_hash * base + ord(text[i])) % mod
    positions = []
    for start in range(n - m + 1):
        if window_hash == pattern_hash:
            # Hash equality is only a candidate; verify every character.
            equal = True
            for j in range(m):
                if text[start + j] != pattern[j]:
                    equal = False
                    break
            if equal:
                positions.append(start)
        if start < n - m:
            window_hash = (window_hash - ord(text[start]) * high) % mod
            window_hash = (window_hash * base + ord(text[start + m])) % mod
    return {"positions": positions}


def suffix(request):
    s = request["text"]
    n = len(s)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    # Prefix doubling: rank each suffix by its first 2*k characters.
    sa = list(range(n))
    rank = [ord(ch) for ch in s]
    k = 1
    while k < n:
        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
        new_rank = [0] * n
        classes = 0
        new_rank[sa[0]] = 0
        for idx in range(1, n):
            a, b = sa[idx - 1], sa[idx]
            key_a = (rank[a], rank[a + k] if a + k < n else -1)
            key_b = (rank[b], rank[b + k] if b + k < n else -1)
            if key_a != key_b:
                classes += 1
            new_rank[b] = classes
        rank = new_rank
        if classes == n - 1:
            break
        k *= 2

    # Kasai's algorithm computes LCP with the previous suffix in SA order.
    inverse = [0] * n
    for i, pos in enumerate(sa):
        inverse[pos] = i
    lcp = [0] * n
    common = 0
    for i in range(n):
        r = inverse[i]
        if r == 0:
            continue
        j = sa[r - 1]
        while i + common < n and j + common < n and s[i + common] == s[j + common]:
            common += 1
        lcp[r] = common
        if common:
            common -= 1
    best_len = max(lcp)
    repeated = ""
    if best_len:
        best_pos = next(sa[i] for i in range(1, n) if lcp[i] == best_len)
        repeated = s[best_pos:best_pos + best_len]
    return {"sa": sa, "lcp": lcp, "repeated": repeated}


def aho(request):
    patterns, texts = request["patterns"], request["texts"]
    # Trie transitions are dictionaries; terminal stores dictionary indices,
    # so duplicate words remain distinct output columns.
    goto = [{}]
    fail = [0]
    terminal = [[]]
    for pattern_index, word in enumerate(patterns):
        state = 0
        for ch in word:
            nxt = goto[state].get(ch)
            if nxt is None:
                nxt = len(goto)
                goto[state][ch] = nxt
                goto.append({})
                fail.append(0)
                terminal.append([])
            state = nxt
        terminal[state].append(pattern_index)

    from collections import deque
    queue = deque()
    bfs_order = [0]
    for child in goto[0].values():
        fail[child] = 0
        queue.append(child)
    while queue:
        state = queue.popleft()
        bfs_order.append(state)
        for ch, child in goto[state].items():
            f = fail[state]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[child] = goto[f].get(ch, 0)
            queue.append(child)

    rows = []
    p = len(patterns)
    for text in texts:
        visits = [0] * len(goto)
        state = 0
        for ch in text:
            while state and ch not in goto[state]:
                state = fail[state]
            state = goto[state].get(ch, 0)
            visits[state] += 1
        # Every visit to a state also represents a match at each failure
        # ancestor. Reverse BFS order propagates counts to failure parents.
        for v in reversed(bfs_order[1:]):
            visits[fail[v]] += visits[v]
        row = [0] * p
        for state, indices in enumerate(terminal):
            if indices:
                count = visits[state]
                for index in indices:
                    row[index] = count
        rows.append(row)
    return {"counts": rows}
