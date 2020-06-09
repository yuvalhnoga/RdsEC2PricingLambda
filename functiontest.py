import json
import boto3
from urllib.request import urlopen
import datetime
import pprint
import os

# json_url = urlopen("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json")
# #json_url = urlopen("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/20200608195020/us-west-1/index.json")
# regionsURL = json.loads(json_url.read())
# now = datetime.datetime.now()
# s3 = boto3.resource('s3')
# # f = open("test.json", "w")
# # f.write(json.dumps(data,indent=1, sort_keys=True))
# region = "eu-west-1"
# print (region)
# region_json = urlopen("https://pricing.us-east-1.amazonaws.com" + regionsURL['regions'][region]['currentVersionUrl'])
# region_load = json.loads(region_json.read())
# filename = region + "_AmazonEC2" + "_" + now.strftime("%Y-%m-%d") + ".json"
# with open(filename, mode='w') as region_file:
#     region_file.write(json.dumps(region_load,indent=1,sort_keys=True))
# os.remove(filename)

poop = "eu-west-1"
nice = poop.replace("-","_")
print (nice)


# for region in regionsURL['regions']:
#     print (region)
#     region_json = urlopen("https://pricing.us-east-1.amazonaws.com" + regionsURL['regions'][region]['currentVersionUrl'])
#     print (region_json)
#     region_load = json.loads(region_json.read())
#     filename = region + "_AmazonEC2" + "_" + now.strftime("%Y-%m-%d") + ".json"
#     with open("/tmp/" + filename, mode='w') as region_file:
#         region_file.write(json.dumps(region_load,indent=1,sort_keys=True))
#     s3.meta.client.upload_file( "/tmp/" + filename, "irelandec2-prices", region + "/" + "EC2/" + filename)