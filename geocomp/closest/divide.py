#!/usr/bin/env python
"""Algoritmo por divisão e conquista"""

from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common import prim
from geocomp.common import guiprim
import math

def compareX(p1, p2):
    if (p1.x == p2.x): return p1.y - p2.y
    return p1.x - p2.x

def compareY(p1, p2):
    if (p1.y == p2.y): return p1.x - p2.x
    return p1.y - p2.y

def swap(v, i , j):
    v[i], v[j] = v[j], v[i]

def partition(v, l, r, compare):
    k = v[r-1]
    j = l-1
    for i in range(l, r-1):
        comp = compare(v[i], k)
        if (comp <= 0):
            j += 1
            swap(v, i, j)
    j += 1
    swap(v, r-1, j)
    return j

def sort_rec(v, l, r, compare):
    if (r > l + 1):
        q = partition(v, l, r, compare)
        sort_rec(v, l, q, compare)
        sort_rec(v, q, r, compare)

def sort(v, compare):
    n = len(v)
    sort_rec(v, 0, n, compare)

def merge(v, l, q, r, compare):
    v1, v2 = [], []
    for i in range(l, q):
        v1.append(v[i])
    for i in range(q, r):
        v2.append(v[i])
    n1, n2 = len(v1), len(v2)

    i, j, k = 0, 0, l

    while (i < n1 and j < n2):
        comp = compare(v1[i], v2[j])
        if (comp <= 0):
            v[k] = v1[i]
            i += 1
        else:
            v[k] = v2[j]
            j += 1
        k += 1
    
    while (i < n1):
        v[k] = v1[i]
        i += 1
        k += 1
    while (j < n2):
        v[k] = v2[j]
        j += 1
        k += 1

def candidates(p, l, r, dmin, pm):
    f = []
    for i in range(l, r):
        if (abs(p[i].x - pm.x) < dmin):
            print("candidate: ", p[i].x, p[i].y)
            f.append(p[i])
    return f

def combine(p, l, r, p1, p2, pm):
    dmin2 = guiprim.dist2(p1, p2)
    dmin = math.sqrt(dmin2)
    print("distancia mínima: ", dmin)
    print("pontos: (", p1.x, p1.y, ") (", p2.x, p2.y, ")")
    f = candidates(p, l, r, dmin, pm)
    t = len(f)
    vl1 = control.plot_vert_line(pm.x)
    vl2 = control.plot_vert_line(pm.x - dmin)
    vl3 = control.plot_vert_line(pm.x + dmin)
    for i in range(t):
        hl1 = control.plot_horiz_line(f[i].y)
        hl2 = control.plot_horiz_line(f[i].y + dmin)
        j = i + 1
        while j < t and (f[j].y - f[i].y) < dmin:
            d = guiprim.dist2(f[i], f[j])
            if (d < dmin2):
                p1, p2, dmin2 = f[i], f[j], d
                update_points(p1, p2)
            j += 1
        control.plot_delete(hl1)
        control.plot_delete(hl2)
    control.plot_delete(vl1)
    control.plot_delete(vl2)
    control.plot_delete(vl3)
    return p1, p2

a, b, id = None, None, None
hia, hib = None, None

def update_points(p1, p2):
    global a, b, id, hia, hib
    if (a != None and b != None):
        if (prim.dist2(p1, p2) >= prim.dist2(a, b)): return
    control.freeze_update()
    if a != None: a.unhilight(hia)
    if b != None: b.unhilight(hib)
    if id != None: control.plot_delete(id)
    a = p1
    b = p2
    hia = a.hilight()
    hib = b.hilight()
    id = a.lineto(b)
    control.thaw_update() 
    control.update()

def divide_rec(p, l, r, compare):
    print(l, r)
    #base
    if r - l == 2:
        sort_rec(p, l, r, compare)
        guiprim.dist2(p[l], p[l+1])
        update_points(p[l], p[l+1])
        return p[l], p[l+1]
    if r - l == 3:
        sort_rec(p, l, r, compare)
        d1 = guiprim.dist2(p[l], p[l+1])
        d2 = guiprim.dist2(p[l], p[l+2])
        d3 = guiprim.dist2(p[l+1], p[l+2])
        if (d1 <= d2 and d1 <= d3): 
            update_points(p[l], p[l+1])
            return p[l], p[l+1]
        if (d2 <= d1 and d2 <= d3):
            update_points(p[l], p[l+2])
            return p[l], p[l+2]
        if (d3 <= d1 and d3 <= d2):
            update_points(p[l+1], p[l+2])
            return p[l+1], p[l+2]
    # 4 points or more
    
    q = (l+r)//2
    pm = p[q] #median point
    print("median point: ", pm.x, pm.y)
    p1, p2 = divide_rec(p, l, q, compare)
    de = prim.dist2(p1, p2)
    p3, p4 = divide_rec(p, q, r, compare)
    dr = prim.dist2(p3, p4)
    p1, p2 = (p1, p2) if (de <= dr) else (p3, p4)
    update_points(p1, p2)
    merge(p, l, q, r, compare)
    return combine(p, l, r, p1, p2, pm)

def Divide (p):
    global a, b, id, hia, hib
    a, b, id, hia, hib = None, None, None, None, None
    sort(p, compareX)
    n = len(p)
    p1, p2 = divide_rec(p, 0, n, compareY)
    p1.hilight()
    p2.hilight()
    print(p1, p2)
    print(math.sqrt(prim.dist2(p1, p2)))
    return p1, p2
