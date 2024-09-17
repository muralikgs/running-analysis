import requests
import login as login
from pandas import json_normalize
import pandas as pd

auth_url = 'https://www.strava.com/oauth/token'
activities_url = 'https://www.strava.com/api/v3/athlete/activities'

payload = {
    'client_id': f'{login.client_id}',
    'client_secret': f'{login.client_secret}',
    'refresh_token': f'{login.refresh_token}',
    'grant_type': 'refresh_token',
    'f': 'json'
}

print('Requesting Token...\n')
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

header = {'Authorization': 'Bearer ' + access_token}

def meters_to_miles(dist):
    return dist / 1609

# The Strava API only supports 200 results per page. This function loops through each page until new_results is empty.
def loop_through_pages(page):
    # start at page ...
    page = page
    # set new_results to True initially
    new_results = True
    # create an empty array to store our combined pages of data in
    data = []
    while new_results:
        # Give some feedback
        print(f'You are requesting page {page} of your activities data ...')
        # request a page + 200 results
        get_strava = requests.get(activities_url, headers=header, params={'per_page': 200, 'page': f'{page}'}).json()
        # save the response to new_results to check if its empty or not and close the loop
        new_results = get_strava
        # add our responses to the data array
        data.extend(get_strava)
        # increment the page
        page += 1
    # return the combine results of our get requests
    return data

def get_cleaned_dataset(start_page=1, activity_type='Run'):
    my_dataset = loop_through_pages(start_page)
    my_cleaned_dataset = []
    for activities in my_dataset:
        if activities['type'] == activity_type:
            my_cleaned_dataset.append(activities)
    
    activities = json_normalize(my_cleaned_dataset)
    df = pd.DataFrame(data=activities)

    return df 
    
def get_gear_info(gear_ids):
    
    gear_info_dict = dict()
    for id in gear_ids: 
        url = 'https://www.strava.com/api/v3/gear/{}'.format(id)
        response = requests.get(url, headers=header)
        model = response.json()
        gear_info_dict[id] = model 
    
    return gear_info_dict