import boto3
import json
import csv
import datetime

regionsDict = {'Africa (Cape Town)': 'af_south_1', 'Asia Pacific (Mumbai)': 'ap_south_1',
               'Asia Pacific (Osaka-Local)': 'osaka_local', 'Asia Pacific (Seoul)': 'ap_northeast_1',
               'Asia Pacific (Singapore)': 'ap_southeast_1', 'Asia Pacific (Sydney)': 'ap_southeast_2',
               'Asia Pacific (Tokyo)': 'ap_northeast_1', 'Canada (Central)': 'ca_central_1',
               'EU (Frankfurt)': 'eu_central_1', 'EU (Ireland)': 'eu_west_1', 'EU (London)': 'eu_west_2',
               'EU (Milan)': 'eu_south_1', 'EU (Paris)': 'eu_west_3', 'EU (Stockholm)': 'eu_north_1',
               'Middle East (Bahrain)': 'me_south_1', 'South America (Sao Paulo)': 'sa_east_1',
               'US East (N. Virginia)': 'us_east_1', 'US East (Ohio)': 'us_east_2', 'US West (Los Angeles)': 'local_la',
               'US West (N. California)': 'us_west_1', 'US West (Oregon)': 'us_west_2'}

def ec2_servicecode(servicecode, region):
    client = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.resource('s3')
    now = datetime.datetime.now()

    response = client.get_products(
        ServiceCode=servicecode,
        Filters=[
            {
                'Field': 'ServiceCode',
                'Type': 'TERM_MATCH',
                'Value': servicecode,
            },
            {
                'Field': 'instanceType',
                'Type': 'TERM_MATCH',
                'Value': 'm5.xlarge',
            },
            {
                'Field': 'location',
                'Type': 'TERM_MATCH',
                'Value': region,
            },
        ],
    )

    filename = regionsDict.get(region) + "_" + servicecode + "_" + now.strftime("%Y-%m-%d") + ".csv"
    with open("/tmp/" + filename, mode='w') as test_file:
        test_writer = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['ServiceCode', 'Location', 'Sku', 'instanceType', 'operatingSystem', 'preInstalledSw', 'USD', 'Description'])

        for PRODUCT in response['PriceList']:
            mydict = json.loads(PRODUCT)
            servicecode = mydict['product']['attributes']['servicecode']
            location = mydict['product']['attributes']['location']
            sku = mydict['product']['sku']
            instanceType = mydict['product']['attributes']['instanceType']
            operatingSystem = mydict['product']['attributes']['operatingSystem']
            preInstalledSw = mydict['product']['attributes']['preInstalledSw']
            first = next(iter(mydict['terms']['OnDemand']))
            second = next(iter(mydict['terms']['OnDemand'][first]['priceDimensions']))
            USD = mydict['terms']['OnDemand'][first]['priceDimensions'][second]['pricePerUnit']['USD']
            description = mydict['terms']['OnDemand'][first]['priceDimensions'][second]['description']
            test_writer.writerow([servicecode, location, sku, instanceType, operatingSystem, preInstalledSw, USD, description])

    s3.meta.client.upload_file( "/tmp/" + filename, "irelandec2-prices", "EC2/" + region + "/" + filename)

def rds_servicecode(servicecode, region):
    client = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.resource('s3')
    now = datetime.datetime.now()

    response = client.get_products(
        ServiceCode=servicecode,
        Filters=[
            {
                'Field': 'ServiceCode',
                'Type': 'TERM_MATCH',
                'Value': servicecode,
            },
            {
                'Field': 'location',
                'Type': 'TERM_MATCH',
                'Value': region,
            },
        ],
    )

    filename = regionsDict.get(region) + "_" + servicecode + "_" + now.strftime("%Y-%m-%d") + ".csv"
    with open("/tmp/" + filename, mode='w') as test_file:
        test_writer = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['ServiceCode', 'Location', 'Sku', 'instanceType', 'USD', 'Description'])

        for PRODUCT in response['PriceList']:
            mydict = json.loads(PRODUCT)
            servicecode = mydict['product']['attributes']['servicecode']
            location = mydict['product']['attributes']['location']
            sku = mydict['product']['sku']
            instanceType = mydict['product']['attributes']['instanceType']
            first = next(iter(mydict['terms']['OnDemand']))
            second = next(iter(mydict['terms']['OnDemand'][first]['priceDimensions']))
            USD = mydict['terms']['OnDemand'][first]['priceDimensions'][second]['pricePerUnit']['USD']
            description = mydict['terms']['OnDemand'][first]['priceDimensions'][second]['description']
            test_writer.writerow([servicecode, location, sku, instanceType, USD, description])

    s3.meta.client.upload_file( "/tmp/" + filename, "irelandec2-prices", "RDS/" + region + "/" + filename)

def lambda_handler(event, context):
    servicecode = "AmazonEC2"
    region = "US East (N. Virginia)"
    #servicecode2 = "AmazonRDS"
    ec2_servicecode(servicecode,region)
    #rds_servicecode(servicecode2,region)
    # for regionName in regionsDict:
    #     ec2_servicecode("AmazonEC2",regionName)
    #     rds_servicecode("AmazonRDS",regionName)
    print ('Finished!')
