exec(open('nogo_strukture.py').read().split("# ---- structure-aware")[0].split("n=200\nprint")[0])
import random,itertools,time
n=200; allp=list(itertools.combinations(range(n),2))
for k in (100,150,200,300):
    rnd=random.Random(k); Fz=rnd.sample(allp,k)
    comps=components(Fz); big=max(len(c) for c in comps)
    t=time.time()
    try:
        v,w,_=count_valid(n,Fz,budget=5_000_000); r=f"{v/N_profile(n,0,0,0):.4e}, korakov {w}"
    except TimeoutError: r="prekinjeno (>5e6 korakov)"
    print(k,"največja gruča konfliktov:",big,"povezav |",r,f"{time.time()-t:.1f}s","| približek",f"{(1-3/(n-1))**k:.4e}")
