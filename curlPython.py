import json
import boto3
from urllib.request import urlopen
import datetime
import pprint
import os


def ec2_servicecode():
    json_url = urlopen("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json")
    regionsURL = json.loads(json_url.read())
    now = datetime.datetime.now()
    s3 = boto3.resource('s3')

    for region in regionsURL['regions']:
        print (region)
        region_json = urlopen("https://pricing.us-east-1.amazonaws.com" + regionsURL['regions'][region]['currentVersionUrl'])
        region_load = json.loads(region_json.read())
        filename = region.replace("-","_") + "_AmazonEC2" + "_" + now.strftime("%Y_%m_%d") + ".json"
        with open("/tmp/" + filename, mode='w') as region_file:
            region_file.write(json.dumps(region_load,indent=1,sort_keys=True))
        s3.meta.client.upload_file( "/tmp/" + filename, "irelandec2-prices", region + "/" + "EC2/" + filename)
        os.remove("/tmp/" + filename)

def rds_servicecode():
    json_url = urlopen("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/region_index.json")
    regionsURL = json.loads(json_url.read())
    now = datetime.datetime.now()
    s3 = boto3.resource('s3')

    for region in regionsURL['regions']:
        print (region)
        region_json = urlopen("https://pricing.us-east-1.amazonaws.com" + regionsURL['regions'][region]['currentVersionUrl'])
        region_load = json.loads(region_json.read())
        filename = region.replace("-","_") + "_AmazonRDS" + "_" + now.strftime("%Y_%m_%d") + ".json"
        with open("/tmp/" + filename, mode='w') as region_file:
            region_file.write(json.dumps(region_load,indent=1,sort_keys=True))
        s3.meta.client.upload_file( "/tmp/" + filename, "irelandec2-prices", region + "/" + "RDS/" + filename)
        os.remove("/tmp/" + filename)


def lambda_handler(event, context):
    ec2_servicecode()
    rds_servicecode()
    print ('Finished!')
