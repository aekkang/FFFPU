'''
LA Hacks 2018, FFFPU
	Takes two segmentation-step result images:
		1) segmentation of image taken from birds-eye
		2) segmentation of image taken at an angle
		3) inches per pixel
		4) dict of category - food
	Calculates approx volume of each segmented object.
'''

import numpy as np

def get_area(seg_matrix, idx):
	return np.count_nonzero(seg_matrix == idx)

def get_heights(seg_matrix, idx):
	min_row = np.where(seg_matrix == idx)[0][0]
	max_row = np.where(seg_matrix == idx)[-1][-1]
	return abs(max_row - min_row)

def simple_estimation(angle, in_p_pxl, foods):
	volumes = []
	for category in foods:
		vol = 2 * np.count_nonzero(angle == category)
		volumes.append(vol)
	return volumes

def volume_estimation(birdseye, angle, in_p_pxl, foods):
	volumes = []
	for category in foods:
		birdseye_h = get_heights(birdseye, category)
		angle_h = get_heights(angle, category)
		height_in = in_p_pxl * (angle_h - birdseye_h)
		height_in = max(height_in, 0.5)
		birdseye_a = get_area(birdseye, category) * (in_p_pxl * in_p_pxl)
		volume = birdseye_a * height_in
		volumes.append(volume)
	return volumes