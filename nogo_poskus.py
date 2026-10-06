import itertools, math, random, time, json
from functools import lru_cache
import numpy as np
C=math.comb
def unrank_comb(m,k,r):
    out=[];x=0
    for left in range(k,0,-1):
        while True:
            c=C(m-x-1,left-1)
            if r<c: out.append(x);x+=1;break
            r-=c;x+=1
    return out
def decode(n,idx):           # labelled rooms of 4, room 1 most significant
    pool=list(range(n));rooms=[]
    R=[C(n-4*t,4) for t in range(n//4)]
    P=[math.prod(R[t+1:]) for t in range(n//4)]
    for t in range(n//4):
        d=idx//P[t]; idx%=P[t]
        pick=unrank_comb(len(pool),4,d); rooms.append([pool[i] for i in pick])
        s=set(pick); pool=[p for i,p in enumerate(pool) if i not in s]
    return rooms
def total(n): return math.factorial(n)//(24**(n//4))
def valid(rooms,F):
    for r in rooms:
        s=set(r)
        for a,b in F:
            if a in s and b in s: return False
    return True
# --- inclusion-exclusion exact count ---
def count_S(n,S):
    # components of graph S
    par={}
    def f(x):
        while par.setdefault(x,x)!=x: x=par[x]
        return x
    for a,b in S: par[f(a)]=f(b)
    comp={}
    for a,b in S:
        for v in (a,b): comp.setdefault(f(v),set()).add(v)
    sizes=[len(c) for c in comp.values()]
    if any(s>4 for s in sizes): return 0
    m=n//4; singles=n-sum(sizes); tot=0
    for assign in itertools.product(range(m),repeat=len(sizes)):
        load=[0]*m
        for s,r in zip(sizes,assign): load[r]+=s
        if max(load)>4: continue
        rem=[4-l for l in load]
        w=math.factorial(singles)
        for x in rem: w//=math.factorial(x)
        tot+=w
    return tot
def incl_excl(n,F):
    tot=0;terms=0;nz=0
    for k in range(len(F)+1):
        for S in itertools.combinations(F,k):
            terms+=1;c=count_S(n,S)
            if c: nz+=1
            tot+=(-1)**k*c
    return tot,terms,nz
def lab_dp(n,F):
    forb=set(F)|{(b,a) for a,b in F}
    @lru_cache(None)
    def g(mask):
        if mask==(1<<n)-1: return 1
        i=next(k for k in range(n) if not mask>>k&1)
        free=[j for j in range(i+1,n) if not mask>>j&1];s=0
        for a,b,c in itertools.combinations(free,3):
            q=(i,a,b,c)
            if any((x,y) in forb for x,y in itertools.combinations(q,2)): continue
            s+=g(mask|1<<i|1<<a|1<<b|1<<c)
        return s
    return g(0)*math.factorial(n//4)
res={}
# 1) single conflict: exact fraction 3/(n-1)
n=12;N=total(n)
for F in ([(0,1)],[(0,11)],[(5,6)]):
    inv=sum(not valid(decode(n,i),F) for i in range(N))
    print("single",F,"invalid",inv,"N*3/(n-1)",N*3//(n-1))
# 2) bitmaps for n=12
random.seed(4)
allp=list(itertools.combinations(range(n),2))
sets={"1 konflikt (0,1)":[(0,1)],"3 konflikti":random.sample(allp,3),"10 konfliktov":random.sample(allp,10)}
maps={}
for name,F in sets.items():
    M=np.array([valid(decode(n,i),F) for i in range(N)]).reshape(495,70)
    maps[name]=(F,M)
    tot,terms,nz=incl_excl(n,F)
    print(name,F,"brute valid",int(M.sum()),"incl-excl",tot,"terms",terms,"nonzero",nz,"dp",lab_dp(n,F))
np.save("/tmp/maps.npy",np.array([m for _,(F,m) in maps.items()]))
json.dump({k:v[0] for k,v in maps.items()},open("/tmp/maps.json","w"))
# 3) scaling: incl-excl vs DP for n=16,20,24 and k conflicts
for n in (16,20,24):
    allp=list(itertools.combinations(range(n),2))
    for k in (4,8,12,16):
        random.seed(n*100+k);F=random.sample(allp,k)
        t=time.time();ie=incl_excl(n,F);tie=time.time()-t
        if n<=20:
            t=time.time();dp=lab_dp(n,F);tdp=time.time()-t
        else: dp,tdp=None,None
        print(n,k,"valid",ie[0],"of",total(n),"frac %.4f"%(ie[0]/total(n)),"terms",ie[1],"nz",ie[2],"t_ie %.3f"%tie,"dp",dp==ie[0] if dp is not None else '-', "t_dp",None if tdp is None else round(tdp,3))
