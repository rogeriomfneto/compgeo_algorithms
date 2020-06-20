#!/usr/bin/env python
"""Algoritmo de Graham"""

from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common import prim
from geocomp.common import guiprim

# Algoritmo de ordenação
def swap(v, i , j):
    v[i], v[j] = v[j], v[i]

def partition(v, l, r, compare):
    k = v[r-1]
    j = l-1
    for i in range(l, r-1):
        comp = compare(v[0], v[i], k)
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
    sort_rec(v, 1, n, compare)

# Funções do Graham
def comparaPontoAngulo(p0, p1, p2):
    if p1 == p2: return 0

    if prim.right(p0, p2, p1) or\
        (prim.collinear(p0, p1, p2) and\
        prim.dist2(p0, p1) < prim.dist2(p0, p2)):
        return -1

    return 1

def comparaPontoExtremo(p1, p2):
	if (p1.y == p2.y): return p1.x - p2.x
	return p1.y - p2.y

def pontoExtremo(points):
	minPoint = 0
	for i in range(len(points)):
		if comparaPontoExtremo(points[i], points[minPoint]) < 0:
			minPoint = i
	return minPoint

def preprocessa(points):
    k = pontoExtremo(points)
    swap(points, 0, k)
    sort(points, comparaPontoAngulo)

def imprimePontos(points):
	# print("Coleção de pontos:")
	for i in range(len(points)):
		print(i, "º: ", points[i], sep="")

def insereSegmento(points, i, j, color='red'):
	return control.plot_segment(points[i].x, points[i].y, points[j].x, points[j].y, color)

def plotHull(points):
    plotIds = []
    plotIds.append(insereSegmento(points, 0, 1))
    plotIds.append(insereSegmento(points, 1, 2))
    plotIds.append(insereSegmento(points, 2, 0))
    points[0].hilight('cyan')
    points[1].hilight('cyan')
    points[2].hilight('cyan')
    control.sleep()
    return plotIds

def atualizaPlotHull(Hull, points, plotIds, k):
    aux = plotIds[-1]
    control.plot_delete(plotIds[-2])
    control.plot_delete(plotIds[-3])
    plotIds.pop(-1)
    plotIds.pop(-1)
    plotIds.pop(-1)
    plotIds.append(insereSegmento(points, Hull[-1], k, 'blue'))
    plotIds.append(aux)
    control.sleep()


def atualizaHull(Hull, points, plotIds, k):
    control.plot_delete(plotIds[-1])
    plotIds.pop(-1)
    plotIds.append(insereSegmento(points, k, Hull[-1], 'blue'))
    plotIds.append(insereSegmento(points, k, 0, 'blue'))
    control.sleep()

    j = len(Hull)-1
    while prim.right_on(points[Hull[j-1]], points[Hull[j]], points[k]) and\
        len(Hull) > 2:
        points[Hull[-1]].unhilight()
        Hull.pop(-1)
        atualizaPlotHull(Hull, points, plotIds, k)
        j -= 1
    Hull.append(k)
    points[Hull[-1]].hilight('cyan')
    control.plot_delete(plotIds[-2])
    plotIds[-2] = insereSegmento(points, Hull[-2], Hull[-1])
    control.sleep()

def Graham(points):
    print("Coleção de pontos:")
    imprimePontos(points)
    preprocessa(points)
    print("\nApós ordenação:")
    imprimePontos(points)

    n = len(points)
    if n < 3: return None

    Hull = [0,1,2]
    plotIds = plotHull(points)
    for k in range(3,n):
        atualizaHull(Hull, points, plotIds, k)
    control.plot_delete(plotIds[-1])
    plotIds[-1] = insereSegmento(points, -1, 0)
    control.sleep()
    print(Hull)
    return Hull
