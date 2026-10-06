import itertools, math, random, time, sys
from collections import defaultdict
sys.setrecursionlimit(10000)
C=math.comb; F=math.factorial
def dfact(x): return math.prod(range(x-1,0,-2)) if x>0 else 1
def P4(r): return F(r)//(24**(r//4)*F(r//4)) if r%4==0 else 0
def N_profile(n,c2,c3,c4):
    """labelled arrangements of n students in n/4 rooms where given disjoint blocks (c2 pairs, c3 triples, c4 quads) each stay in one room"""
    m=n//4; s=n-2*c2-3*c3-4*c4
    if s<0: return 0
    U=0
    for j in range(c2//2+1):
        c2r=c2-2*j
        need=c3+2*c2r
        if need>s: continue
        ways=C(c2,2*j)*dfact(2*j)
        ways*=F(s)//F(s-c3)                      # one singleton per triple
        r=s-c3
        ways*=F(r)//(F(r-2*c2r)*2**c2r)          # two singletons per remaining pair
        ways*=P4(r-2*c2r)
        U+=ways
    return U*F(m)
# brute verification of N_profile against simple count (n=12,16)
import nogo_ref as R
for n in (12,16):
    for prof in [(1,0,0),(2,0,0),(0,1,0),(1,1,0),(0,0,1),(3,0,0),(2,1,0)]:
        c2,c3,c4=prof; S=[];v=0
        for _ in range(c2): S.append((v,v+1)); v+=2
        for _ in range(c3): S+= [(v,v+1),(v+1,v+2)]; v+=3
        for _ in range(c4): S+= [(v,v+1),(v+1,v+2),(v+2,v+3)]; v+=4
        assert R.count_S(n,S)==N_profile(n,*prof),(n,prof)
print("N_profile verified")

def components(edges):
    adj=defaultdict(list)
    for i,(a,b) in enumerate(edges): adj[a].append(i); adj[b].append(i)
    seen=set(); comps=[]
    for i in range(len(edges)):
        if i in seen: continue
        stack=[i]; ce=[]; seen.add(i)
        while stack:
            e=stack.pop(); ce.append(e)
            for v in edges[e]:
                for f in adj[v]:
                    if f not in seen: seen.add(f); stack.append(f)
        comps.append([edges[e] for e in ce])
    return comps
def comp_poly(cedges, budget):
    """signed counts of edge subsets of one conflict component, keyed by block profile; prune when a block exceeds 4 vertices"""
    poly=defaultdict(int); visited=[0]
    E=cedges; L=len(E)
    def rec(i, par, sign):
        visited[0]+=1
        if visited[0]>budget: raise TimeoutError
        if i==L:
            sizes=defaultdict(int)
            for v in par: sizes[find(par,v)]+=1
            c=[0,0,0]
            for r,sz in sizes.items():
                if sz>=2: c[sz-2]+=1
            poly[tuple(c)]+=sign; return
        rec(i+1, par, sign)                       # edge not taken
        a,b=E[i]; p2=dict(par); p2.setdefault(a,a); p2.setdefault(b,b)
        ra,rb=find(p2,a),find(p2,b)
        if ra!=rb:
            p2[ra]=rb
            if sum(1 for v in p2 if find(p2,v)==rb)>4: return   # block too big -> weight 0 for all supersets
        rec(i+1, p2, -sign)
    def find(p,x):
        while p[x]!=x: x=p[x]
        return x
    rec(0,{},1)
    return poly, visited[0]
def count_valid(n,edges,budget=3_000_000):
    total=defaultdict(int); total[(0,0,0)]=1; work=0
    for ce in components(edges):
        poly,w=comp_poly(ce,budget); work+=w
        new=defaultdict(int)
        for k1,v1 in total.items():
            for k2,v2 in poly.items():
                k=(k1[0]+k2[0],k1[1]+k2[1],k1[2]+k2[2]); new[k]+=v1*v2
        total={k:v for k,v in new.items() if v}
    return sum(v*N_profile(n,*k) for k,v in total.items()), work, len(total)

# verify against DP / incl-excl for n=16,20
for n in (16,20):
    allp=list(itertools.combinations(range(n),2))
    for k in (8,12,16):
        random.seed(n*100+k); Fz=random.sample(allp,k)
        v,_,_=count_valid(n,Fz); ie=R.incl_excl(n,Fz)[0]
        assert v==ie,(n,k)
print("count_valid verified vs inclusion-exclusion")

def structures(n,k,seed=1):
    rnd=random.Random(seed); V=list(range(n)); rnd.shuffle(V)
    out={}
    out["disjunktni pari"]=[(V[2*i],V[2*i+1]) for i in range(k)]
    out["veriga"]=[(V[i],V[i+1]) for i in range(k)]
    out["zvezda"]=[(V[0],V[i+1]) for i in range(k)]
    g=[];i=0
    while len(g)<k: a,b,c=V[3*i:3*i+3]; g+= [(a,b),(b,c),(a,c)]; i+=1
    out["skupine po 3 (vsi proti vsem)"]=g[:k]
    allp=list(itertools.combinations(range(n),2))
    out["naključni"]=rnd.sample(allp,k)
    return out
n=200
print(f"\nn={n} študentov (ena spol), {n//4} sob; N = {N_profile(n,0,0,0):.3e}")
print("struktura | k | delež veljavnih | približek (1-3/(n-1))^k | naivnih členov 2^k | dejanskih korakov | čas")
for k in (10,30,60,100):
    for name,Fz in structures(n,k).items():
        t=time.time()
        try:
            v,work,prof=count_valid(n,Fz); tt=time.time()-t
            frac=v/N_profile(n,0,0,0)
            print(f"{name} | {k} | {frac:.4e} | {(1-3/(n-1))**k:.4e} | 2^{k} | {work} | {tt:.2f}s")
        except TimeoutError:
            print(f"{name} | {k} | — | {(1-3/(n-1))**k:.4e} | 2^{k} | >3e6 (prekinjeno) | {time.time()-t:.1f}s")

# ---- structure-aware formulas (no enumeration) ----
def path_poly(L):
    # signed sum over edge subsets of a path with L edges; runs of r taken edges -> block of r+1 vertices (r<=3)
    from collections import defaultdict
    st={(0,(0,0,0)):1}   # (current run length, profile) -> signed count
    for _ in range(L):
        new=defaultdict(int)
        for (run,p),v in st.items():
            # not take: close run
            q=list(p)
            if run: q[run-1]+=1
            new[(0,tuple(q))]+=v
            if run<3: new[(run+1,p)]-=v
        st=new
    out=defaultdict(int)
    for (run,p),v in st.items():
        q=list(p)
        if run: q[run-1]+=1
        out[tuple(q)]+=v
    return out
def star_poly(d):
    return {(0,0,0):1,(1,0,0):-d,(0,1,0):C(d,2),(0,0,1):-C(d,3)}
def valid_from_poly(n,poly): return sum(v*N_profile(n,*k) for k,v in poly.items())
# verify vs enumeration on small
for L in (3,6,9):
    Fz=[(i,i+1) for i in range(L)]
    assert valid_from_poly(24,path_poly(L))==count_valid(24,Fz)[0]
for d in (3,6,9):
    Fz=[(0,i+1) for i in range(d)]
    assert valid_from_poly(24,star_poly(d))==count_valid(24,Fz)[0]
print("\npath/star formulas verified")
NT=N_profile(n,0,0,0)
for k in (30,60,100,150):
    t=time.time(); a=valid_from_poly(n,path_poly(k))/NT; ta=time.time()-t
    t=time.time(); b=valid_from_poly(n,star_poly(k))/NT if k<n else None; tb=time.time()-t
    print(f"k={k}: veriga {a:.4e} ({ta:.2f}s) | zvezda {b:.4e} ({tb:.3f}s) | približek {(1-3/(n-1))**k:.4e}")
