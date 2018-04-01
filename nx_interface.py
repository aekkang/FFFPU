'''
LA Hacks 2018, FFFPU
	Takes input list of foods and their servings.
	Makes HTTP request to Nutritionix to get nutritional
	information for the input foods.
	Scale factors of interest [calorie count, sodium] by
	the serving_amnt / nutritionix_amnt.
	Return data in the form of a list of dicts for each food
	containing the relevant information.
'''

import requests
from requests.auth import HTTPBasicAuth
import argparse
from json import dumps

NX_ENDPOINT = "https://trackapi.nutritionix.com/v2/natural/nutrients"
CUBINCH_TO_CUP = 0.06926

def get_auth_headers():
	with open('nutritionix_keys', 'r') as key_file:
		app_id = key_file.readline().strip()
		app_key = key_file.readline().strip()
	headers = {
		'content-type' : 'application/json',
		'x-app-id' : app_id,
		'x-app-key' : app_key,
		'x-remote-user-id' : '0'
	}
	return headers

def make_query(foods):
	# TODO: figure out how the input is structured
	return ' '.join(foods)

def check_if_cups(food_result):
	if food_result["serving_qty"] == "cup":
		return True, food_result["serving_weight_grams"]
	other_measures_lst = food_result["alt_measures"]
	for measures in other_measures_lst:
		if measures["measure"] == "cup":
			return True, measures["serving_weight"]
	return False, 0.0

def parse_results(results, volumes):
	output = []
	for i, result in enumerate(results):

		# print(result)
		# Just get the calorie count, sodium, and serving size for now
		food_name = result["food_name"]
		calories = float(result["nf_calories"])
		sodium = float(result["nf_sodium"]) 

		# Check if it's a food type that has a cup measurement.
		# TODO: probably add functionality for other types of measurement,
		# i.e. cookies are measured per diameter
		has_cups, grams_p_cup = check_if_cups(result)
		if has_cups:
			volume_in_cups = volumes[i] * CUBINCH_TO_CUP
			serving_ratio = float(grams_p_cup) / float(result["serving_weight_grams"])
			calories = calories * volume_in_cups * serving_ratio
			sodium = sodium * volume_in_cups * serving_ratio

		result_dict = {
			"name" : food_name,
			"calories" : calories,
			"sodium" : sodium
		}
		output.append(result_dict)
	return output

def nutritional_info(foods, volumes):
	headers = get_auth_headers()
	results = []
	for food in foods:
		query_string = make_query([food])
		data = { 'query' : query_string }
		result = requests.post(url = NX_ENDPOINT, data = dumps(data), headers = headers)
		try:
			result.raise_for_status()
			query_result = parse_results(result.json()["foods"], volumes)
			results.extend(query_result)
		except:
			pass
	return results
	