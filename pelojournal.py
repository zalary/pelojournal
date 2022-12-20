import requests
import json
import time, datetime
import os
import subprocess

from datetime import date, timedelta

s = requests.Session()
peloton_user = os.environ['PELOTON_USER']
peloton_pass = os.environ['PELOTON_PASS']
payload = {'username_or_email':peloton_user, 'password':peloton_pass}
s.post('https://api.onepeloton.com/auth/login', json=payload)

user = s.get('https://api.onepeloton.com/api/me')
user_json = json.loads(user.text)
# print(json.dumps(forme, indent=2))

user_id = user_json['id']
# print(user_id)

# the zulu time here is almost certainly based on your own timezone.
# use dev tools in the browser to confirm your date format
user_date = input("Which date do you wish to import (MM/DD/YY): ")
if user_date:
    start = datetime.datetime.strptime(user_date, '%m/%d/%y').date()
else:
    start =  date.today() 
# print ("date_today: ", date.today())
# print("user_date:", user_date)

print(start)
start_zulu = start.isoformat() + 'T06:00:00.000Z'
print(start_zulu)
end = start + datetime.timedelta(days = 1)
end_zulu = end.isoformat() + 'T06:00:00.000Z'
# print(start_zulu)
# print(end_zulu)

# get only today's workouts
# using our user id and formatted dates.
today_workouts = "https://api.onepeloton.com/api/user/{}/workouts?joins=ride&limit=10&page=0&from={}&to={}".format(user_id, start_zulu, end_zulu)

# # wo_url = "https://api.onepeloton.com/api/user/{}/workouts?limit=10&page=0".format(u_id)
workout_list = s.get(today_workouts)
workout_json = json.loads(workout_list.text)
print(json.dumps(workout_json, indent=2))

for i in workout_json['data']:
    instructor_lookup = "https://api.onepeloton.com/api/instructor/{}".format(i['ride']['instructor_id'])
    instructor = s.get(instructor_lookup)
    instructor_json = json.loads(instructor.text)
    #print(json.dumps(instructor_json, indent=2))

    workout_name = (i['name'])
    instructor_name = instructor_json['name']
    workout_start = datetime.datetime.fromtimestamp( i['created_at'] )
    workout_length = str(datetime.timedelta(seconds=i['ride']['duration']))
    print (workout_name)
    print(instructor_name)
    print (workout_length)
    print(workout_start)
    text = '''
    {0}
    {1}
    {2}
    '''.format(workout_name,instructor_name,workout_length)

    # s = 'dayone2 -j Fitness --d="{}" new "{}" -t peloton'.format(workout_start, text)
    # os.system(s)

    # Using system() method to
    # execute shell commands
    subprocess.Popen('dayone2 -j Fitness --d="{}" new "{}" -t peloton'.format(workout_start, text), shell=True)


