def fibonacci(n): 
    u = [0, 1] 
    for i in range(2, n+1): 
        u.append(u[i-1]+u[i-2]) 
    return u[n] 
v = -3
r = fibonacci(v) 
print(r)