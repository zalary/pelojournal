import argparse
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

parser = argparse.ArgumentParser(
    prog="pelojournal",
    description="Post your Peloton workouts to your DayOne journal",
    epilog="Thanks for using %(prog)s! :)",
)

parser.add_argument('-d', '--date', help='optional: the date of workouts you want to import, in MM/DD/YY format (defaults to today)')
args = vars(parser.parse_args())

if args['date']: 
    # print(args['date'])
    user_date = args['date']
    start = datetime.datetime.strptime(user_date, '%m/%d/%y').date()
else:
    start =  date.today() 
print ("date_today: ", date.today())

# print("start: ", start)
start_zulu = start.isoformat() + 'T06:00:00.000Z'
# print("start_zulu: ", start_zulu)
end = start + datetime.timedelta(days = 1)
end_zulu = end.isoformat() + 'T06:00:00.000Z'
# print(end_zulu)

# get only today's workouts
# using our user id and formatted dates.
today_workouts = "https://api.onepeloton.com/api/user/{}/workouts?joins=ride&limit=10&page=0&from={}&to={}".format(user_id, start_zulu, end_zulu)

# # wo_url = "https://api.onepeloton.com/api/user/{}/workouts?limit=10&page=0".format(u_id)
workout_list = s.get(today_workouts)
workout_json = json.loads(workout_list.text)
print(json.dumps(workout_json, indent=2))

workouts_array = []
for i in workout_json['data']:
    instructor_lookup = "https://api.onepeloton.com/api/instructor/{}".format(i['ride']['instructor_id'])
    instructor = s.get(instructor_lookup)
    instructor_json = json.loads(instructor.text)
    #print(json.dumps(instructor_json, indent=2))

    workout_name = (i['ride']['title'])
    instructor_name = instructor_json['name']
    workout_start = datetime.datetime.fromtimestamp( i['created_at'] )
    device = (i['device_type'])
    workout_length = str(datetime.timedelta(seconds=i['ride']['duration']))
    workouts_array.insert(0, [workout_name, instructor_name, workout_length, workout_start, device])
    print(workouts_array)

workout_list = ["Peloton Workouts"]
for w in workouts_array:
    if (w[4]) == "iPhone" or (w[4]) == "iPad":
        # print(workouts_array)
        workout_name = (w[0])
        instructor_name = (w[1])
        workout_length = (w[2])
        workout_start = (w[3])
        text = '''

{0} - {1}'''.format(workout_name,instructor_name)
        # figure out how to prepend
        # https://linuxhint.com/python-prepend-list/
        workout_list.append(text)

        workout_text = "\n".join(workout_list)
        print(workout_text)
# This throws an error on each post, but is successful
s = 'dayone2 -j Fitness --d="{}" new "{}" -t peloton'.format(workout_start, workout_text)
os.system(s)
