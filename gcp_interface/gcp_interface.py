import requests
import base64
import json
import re

API_KEY = 'gcp_api_key.txt'
TEST_IMGS = ['gcp_examples/' + i for i in ['burger.jpg', 'chips.jpg', 'fries.jpg', 'pie.jpg', 'ramen.jpg', 'sandwich.jpg']]
BLACKLIST = ['[a-z ]*food', '[a-z ]*dish', '[a-z ]*cuisine', 'snack', 'ingredient', 'flavor', 'baking', 'baked goods']


# Encode an image to a base64-encoded string.
def image_to_b64(filename):
    with open(filename, 'rb') as f:
        img = f.read()
        b64 = base64.b64encode(img).decode('UTF-8')

    return b64

# Format image and API key.
def parse_inputs(api_key_filename, img_filename):
    with open(api_key_filename) as f:
        api_key = f.read()
    b64 = image_to_b64(img_filename)

    return api_key, b64

# Call the API and get parsed results.
def call_api(api_key, b64):
    # API call!
    response = requests.post('https://vision.googleapis.com/v1/images:annotate?key=%s' % api_key,
        json = {'requests': [{
            'image': {'content': b64},
            'features': [{'type': 'LABEL_DETECTION', 'maxResults': '10'}]}
        ]})

    # Get and parse API call results.
    results = json.loads(response.text)['responses'][0]['labelAnnotations']
    results = [(result['description'], result['score']) for result in results]
    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results

# Refine the results of an API call.
def refine_results(results):
    refined = []

    for result in results:
        valid = True

        for blackitem in BLACKLIST:
            if re.match(blackitem, result[0]) is not None:
                valid = False

        if valid:
            refined.append(result[0])

    return refined

# Main function!
# 
# To use, provide the filename that contains the API key
# and the filename that contains the image as arguments.
# The output is a list of candidate foods of the image.
#
# See section below for usage.
def main(api_key_filename, img_filename):
    api_key, b64 = parse_inputs(api_key_filename, img_filename)
    results = call_api(api_key, b64)
    results = refine_results(results)

    return results


if __name__ == '__main__':
    for TEST_IMG in TEST_IMGS:
        results = main(API_KEY, TEST_IMG)
        print()
        print('Results of API call on %s' % TEST_IMG)
        print('=' * 50)
        print(results)

    print()
