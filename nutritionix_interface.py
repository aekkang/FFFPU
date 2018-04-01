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

def parse_results(results, volumes):
	output = []
	for i, result in enumerate(results):
		# Just get the calorie count, sodium, and serving size for now
		food_name = result["food_name"]
		if result["serving_unit"] == "cup":
			volume_in_cups = volumes[i] * CUBINCH_TO_CUP
			grams_p_serving = result["serving_weight_grams"]
			food_weight = volume_in_cups * grams_p_serving
			serving_ratio = food_weight / grams_p_serving
		else: 
			serving_ratio = 1.0

		calories = float(result["nf_calories"]) * serving_ratio
		sodium = float(result["nf_sodium"]) * serving_ratio
		result_dict = {
			"name" : food_name,
			"calories" : calories,
			"sodium" : sodium
		}
		output.append(result_dict)
	return output

def nutritional_info(foods, volumes):
	headers = get_auth_headers()
	query_string = make_query(foods)
	print query_string
	data = { 'query' : query_string }
	result = requests.post(url = NX_ENDPOINT, data = dumps(data), headers = headers)
	result.raise_for_status()
	return parse_results(result.json()["foods"], volumes)
	