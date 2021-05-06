import numpy as np

#L1  = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
L1  = [0, 1, 1, 0, 1, 0, 0, 0, 0, 0]
L2  = [1, 0, 0, 1, 0, 0, 0, 0, 0, 0]
#L3  = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
L3  = [0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
L4  = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
L5  = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0]
L6  = [0, 0, 0, 0, 0, 0, 1, 1, 0, 0]
L7  = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
L8  = [0, 0, 0, 0, 0, 0, 1, 0, 1, 0]
L9  = [0, 0, 0, 0, 0, 0, 1, 0, 0, 1]
L10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

L = np.array([L1, L2, L3, L4, L5, L6, L7, L8, L9, L10])

#L1 = [0, 1, 1, 0]
#L2 = [0, 0, 0, 1]
#L3 = [0, 1, 0, 1]
#L4 = [0, 0, 0, 1]
#L = np.array([L1, L2, L3, L4])

length = len(L)
ITERATIONS = 100

def getM(L):
    M = np.zeros([length, length], dtype=float)
    # number of outgoing links
    c = np.zeros([length], dtype=int)
    
    ## TODO 1 compute the stochastic matrix M
    for i in range(0, length):
        c[i] = sum(L[i])
    
    for i in range(0, length):
        for j in range(0, length):
            if L[j][i] == 0: 
                M[i][j] = 0
            else:
                M[i][j] = 1.0/c[j]
    return M

def getTrustrank(M, L, t):
    d = np.zeros([len(L)], dtype=float)
    d = t/np.sum(t)
    t.transpose()
    for _ in range(ITERATIONS):
        t = q*d + (1-q) * M.dot(t)
    t = t/sum(t[:])
    return t

print("Matrix L (indices)")
print(L)    

M = getM(L)
print("Matrix M (stochastic matrix)")
print(M)

### TODO 2: compute pagerank with damping factor q = 0.15
### Then, sort and print: (page index (first index = 1 add +1) : pagerank)
### (use regular array + sort method + lambda function)
print("PAGERANK")
q = 0.15
pr = np.zeros([len(L)], dtype=[('x', 'int'), ('y', 'float')])

v = np.zeros((len(L),1))
v += 1/len(L)
v.transpose()
for _ in range(ITERATIONS):
    v = q + (1-q) * M.dot(v)
v = v/sum(v[:])

for (i, element) in enumerate(v):
    pr[i] = (i+1, element)
pr = sorted (pr, key=lambda x:x[1], reverse = True)
for p in pr:
    print (p[0], ":", p[1])
    
### TODO 3: compute trustrank with damping factor q = 0.15
### Documents that are good = 1, 2 (indexes = 0, 1)
### Then, sort and print: (page index (first index = 1, add +1) : trustrank)
### (use regular array + sort method + lambda function)
print("TRUSTRANK (DOCUMENTS 1 AND 2 ARE GOOD)")
q = 0.15
tr = np.zeros([len(L)], dtype=[('x', 'int'), ('y', 'float')])

t = np.zeros([len(L)], dtype=float)
t[0] = 1
t[1] = 1
t = getTrustrank(M, L, t)

for (i, element) in enumerate(t):
    tr[i] = (i+1, element)
tr = sorted (tr, key=lambda x:x[1], reverse = True)
for el in tr:
    print (el[0], ":", el[1])

### TODO 4: Repeat TODO 3 but remove the connections 3->7 and 1->5 (indexes: 2->6, 0->4) 
### before computing trustrank
print("TRUSTRANK (DOCUMENTS 1 AND 2 ARE GOOD, 3->7 AND 1->5 REMOVED")
L1  = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
L3  = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
L = np.array([L1, L2, L3, L4, L5, L6, L7, L8, L9, L10])
M = getM(L)
t = np.zeros([len(L)], dtype=float)
t[0] = 1
t[1] = 1
t = getTrustrank(M, L, t)
for (i, element) in enumerate(t):
    tr[i] = (i+1, element)
tr = sorted (tr, key=lambda x:x[1], reverse = True)
for el in tr:
    print (el[0], ":", el[1])
