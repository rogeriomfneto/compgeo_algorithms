#!/usr/bin/env python
"""Algoritmo embrulho de presente"""

from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common import prim
from geocomp.common import guiprim

def comparePoint(p1, p2):
	if (p1.y == p2.y): return p1.x - p2.x
	return p1.y - p2.y

def pontoExtremo(points):
	minPoint = 0
	for i in range(len(points)):
		if comparePoint(points[i], points[minPoint]) < 0:
			minPoint = i
	return minPoint

def proximoPonto(k, points):
	n = len(points)
	i = (k + 1)%n

	id_proximo_segmento = insereSegmento(k, i, points, 'blue')
	control.sleep()
	for j in range(n):
		if j == k: continue
		id_segmento_temporario = insereSegmento(k, j, points, 'yellow')
		control.sleep()
		if prim.right(points[k], points[i], points[j]) or\
		   	(prim.collinear(points[k], points[i], points[j]) and\
		   	prim.dist2(points[k], points[j]) > prim.dist2(points[k], points[i])):
		   i = j
		   control.plot_delete(id_proximo_segmento)
		   control.sleep()
		   id_proximo_segmento = insereSegmento(k, i, points, 'blue')

		control.plot_delete(id_segmento_temporario)
	control.plot_delete(id_proximo_segmento)
	return i

def insereSegmento(i, j, points, color='red'):
	return control.plot_segment(points[i].x, points[i].y, points[j].x, points[j].y, color)

def imprimePontos(points):
	print("Coleção de pontos:")
	for i in range(len(points)):
		print(i, "º: ", points[i], sep="")

def Embrulho(points):
	imprimePontos(points)
	Hull = []
	k = pontoExtremo(points)
	Hull.append(k)
	points[k].hilight('cyan')
	i = proximoPonto(k, points)
	# points[k].unhilight()
	while (k != i):
		Hull.append(i)
		insereSegmento(Hull[-1], Hull[-2], points)
		points[i].hilight('cyan')
		i = proximoPonto(i, points)
		# points[i].unhilight(id)

	insereSegmento(Hull[-1], Hull[-0], points)
	print("Fecho convexo:", Hull, "\n")
	return Hull
	
		
	
