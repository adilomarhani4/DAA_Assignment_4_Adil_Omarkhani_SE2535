import random
import unittest
from Python.source import algorithms as a


class Assignment4Tests(unittest.TestCase):
    def test_lcs(self):
        r = a.lcs({"a":"tea_time", "b":"team"})
        self.assertEqual(r["length"], 4)
        self.assertEqual(len(r["sequence"]), 4)
        for s in ("tea_time", "team"):
            it = iter(s)
            self.assertTrue(all(any(c == x for x in it) for c in r["sequence"]))
        self.assertEqual(a.lcs({"a":"", "b":"abc"}), {"length":0,"sequence":""})

    def test_merge_and_plan(self):
        r = a.merge({"sizes":[2,3,4]})
        self.assertEqual(r["cost"],14)
        self.assertEqual(len(r["plan"]),2)
        active = {(i,i): sizes for i,sizes in enumerate([2,3,4])}
        for l,k,rr in r["plan"]:
            self.assertIn((l,k),active)
            self.assertIn((k+1,rr),active)
            total = active.pop((l,k)) + active.pop((k+1,rr))
            active[(l,rr)] = total
        self.assertEqual(len(active),1)
        self.assertEqual(a.merge({"sizes":[]}), {"cost":0,"plan":[]})

    def test_tree(self):
        self.assertEqual(a.tree({"n":3,"weights":[4,9,6],"edges":[[0,1],[1,2]]})["weight"],10)
        self.assertEqual(a.tree({"n":3,"weights":[-1,-2,-3],"edges":[[0,1],[1,2]]}), {"weight":0,"selected":[]})
        n=20000
        r=a.tree({"n":n,"weights":[1]*n,"edges":[[i,i+1] for i in range(n-1)]})
        self.assertEqual(r["weight"],(n+1)//2)
        chosen=set(r["selected"])
        self.assertEqual(len(chosen),r["weight"])
        self.assertFalse(any(i+1 in chosen for i in chosen if i+1<n))

    def test_searches(self):
        cases=[("", ""), ("", "a"), ("aaaaa","aaa"), ("abababa","aba"),
               ("abdj","ab"), ("abc","long"), ("Aa! Aa!","Aa!")]
        for text,pattern in cases:
            expected=a.naive({"text":text,"pattern":pattern})
            self.assertEqual(a.kmp({"text":text,"pattern":pattern}),expected)
            self.assertEqual(a.rk({"text":text,"pattern":pattern}),expected)
        self.assertEqual(a.rk({"text":"abdj","pattern":"ab"}),{"positions":[0]})

    def test_suffix(self):
        for s in ["", "a", "aaaa", "banana", "abcdef", "ababab", "mississippi"]:
            r=a.suffix({"text":s})
            self.assertEqual(sorted(r["sa"]),list(range(len(s))))
            self.assertEqual(r["lcp"][0:1],[0] if s else [])
            self.assertEqual(r["sa"],sorted(range(len(s)),key=lambda i:s[i:]))
            expected=max((s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1)
                          if any(s[k:k+j-i]==s[i:j] for k in range(len(s)-(j-i)+1) if k!=i)),key=len,default="")
            self.assertEqual(len(r["repeated"]),len(expected))

    def test_aho(self):
        self.assertEqual(a.aho({"patterns":["he","she","he"],"texts":["sheshe","sheshe",""]}),
                         {"counts":[[2,2,2],[2,2,2],[0,0,0]]})
        self.assertEqual(a.aho({"patterns":[],"texts":["","abc"]}),{"counts":[[],[]]})
        self.assertEqual(a.aho({"patterns":["a","aa","aaa"],"texts":["aaaa",""]}),
                         {"counts":[[4,3,2],[0,0,0]]})

    def test_random_search_equivalence(self):
        rng=random.Random(20261108)
        alphabet="abca !"
        for _ in range(300):
            text="".join(rng.choice(alphabet) for _ in range(rng.randrange(25)))
            pattern="".join(rng.choice(alphabet) for _ in range(rng.randrange(10)))
            q={"text":text,"pattern":pattern}
            expected=a.naive(q)
            self.assertEqual(a.kmp(q),expected)
            self.assertEqual(a.rk(q),expected)


if __name__ == "__main__":
    unittest.main()
