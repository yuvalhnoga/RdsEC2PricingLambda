import boto3
import json
import csv
import datetime
import pprint
import os

regionsDict = {'Africa (Cape Town)': 'af_south_1', 'Asia Pacific (Hong Kong)': 'ap_east_1', 'Asia Pacific (Mumbai)': 'ap_south_1',
            'Asia Pacific (Osaka-Local)': 'ap_northeast_3', 'Asia Pacific (Seoul)': 'ap_northeast_2',
            'Asia Pacific (Singapore)': 'ap_southeast_1', 'Asia Pacific (Sydney)': 'ap_southeast_2',
            'Asia Pacific (Tokyo)': 'ap_northeast_1', 'Canada (Central)': 'ca_central_1',
            'EU (Frankfurt)': 'eu_central_1', 'EU (Ireland)': 'eu_west_1', 'EU (London)': 'eu_west_2',
            'EU (Milan)': 'eu_south_1', 'EU (Paris)': 'eu_west_3', 'EU (Stockholm)': 'eu_north_1',
            'Middle East (Bahrain)': 'me_south_1', 'South America (Sao Paulo)': 'sa_east_1',
            'US East (N. Virginia)': 'us_east_1', 'US East (Ohio)': 'us_east_2', 'US West (Los Angeles)': 'local_la',
            'US West (N. California)': 'us_west_1', 'US West (Oregon)': 'us_west_2'}

def translate_reserved_terms(term_attributes):
    lease_contract_length = term_attributes.get('LeaseContractLength')
    purchase_option = term_attributes.get('PurchaseOption')
    offering_class = term_attributes.get('OfferingClass')
    leases = {'1yr': '1yrTerm',
            '3yr': '3yrTerm'}
    # options = {'All Upfront': 'allUpfront',
    #            'AllUpfront': 'allUpfront',
    #            'Partial Upfront': 'partialUpfront',
    #            'No Upfront': 'noUpfront'}
    return leases[lease_contract_length] + str(offering_class).capitalize() + '.' + str(purchase_option.replace(' ','')) 

def format_price(price):
    return str(float("%f" % float(price))).rstrip('0').rstrip('.')

def get_reserved_pricing(terms):
    pricing = {}
    reserved_terms = terms.get('Reserved', {})
    for reserved_term in reserved_terms.keys():
        term_attributes = reserved_terms.get(reserved_term).get('termAttributes')
        price_dimensions = reserved_terms.get(reserved_term).get('priceDimensions')
        # No Upfront instances don't have price dimension for upfront price
        upfront_price = 0.0
        price_per_hour = 0.0
        for price_dimension in price_dimensions.keys():
            temp_price = price_dimensions.get(price_dimension).get('pricePerUnit').get('USD')
            if price_dimensions.get(price_dimension).get('unit') == 'Hrs':
                price_per_hour = temp_price
            else:
                upfront_price = temp_price
        local_term = translate_reserved_terms(term_attributes)
        #lease_in_years = term_attributes.get('LeaseContractLength')[0]
        #hours_in_term = int(lease_in_years[0]) * 365 * 24
        #price = float(price_per_hour) + (float(upfront_price)/hours_in_term)
        price = float(price_per_hour)
        pricing[local_term] = format_price(price)
        pricing[local_term + ".Fee"] = format_price(upfront_price)
    return pricing

def writeReserved(reserved_dict, location, sku, instanceType, operatingSystem, preInstalledSw, file):
    for reserved_type in reserved_dict.keys():
        if "Fee" not in reserved_type:
            file.writerow([location, sku, instanceType, operatingSystem, preInstalledSw.replace(' ','_'), reserved_type, reserved_dict[reserved_type], reserved_dict[reserved_type + ".Fee"]])

def writeReservedRDS(reserved_dict, location, sku, instanceType, deploymentOption, file):
    for reserved_type in reserved_dict.keys():
        if "Fee" not in reserved_type:
            file.writerow([location, sku, instanceType, deploymentOption.replace('-','_'), reserved_type, reserved_dict[reserved_type], reserved_dict[reserved_type + ".Fee"]])

def ec2_servicecode(servicecode,region):
    client = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.resource('s3')
    #now = datetime.datetime.now()

    response = client.get_products(
        ServiceCode='AmazonEC2',
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

    filename = regionsDict.get(region) + "_" + servicecode + ".csv"
    test_file = open("/tmp/" + filename, mode='w')
    test_writer = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    test_writer.writerow(['Region', 'SKU', 'InstanceType', 'operationSystem', 'preInstalledSW', 'Pricing' 'Plan', 'Hourly', 'Upfront'])

    for PRODUCT in response['PriceList']:
        mydict = json.loads(PRODUCT)
        product_name = mydict.get('product')
        if product_name.get('productFamily') not in ['Compute Instance', 'Compute Instance (bare metal)', 'Dedicated Host']:
            continue
        servicecode = mydict['product']['attributes']['servicecode']
        location = mydict['product']['attributes']['location']
        sku = mydict['product']['sku']
        instanceType = mydict['product']['attributes']['instanceType']
        operatingSystem = mydict['product']['attributes']['operatingSystem']
        preInstalledSw = mydict['product']['attributes']['preInstalledSw']
        terms = mydict.get('terms')
        ondemand_terms = terms.get('OnDemand',{})
        priceOnDemand = 0.0
        
        for ondemand_term in ondemand_terms:
            price_dimensions = ondemand_terms.get(ondemand_term).get('priceDimensions')
            for price_dimension in price_dimensions.keys():
                priceOnDemand = price_dimensions.get(price_dimension).get('pricePerUnit').get('USD')
        test_writer.writerow([regionsDict[location], sku, instanceType, operatingSystem, preInstalledSw.replace(' ','_'), 'OnDemand' , str(priceOnDemand).rstrip('0').rstrip('.'), '0'])

        reserved_terms = terms.get('Reserved', {})
        if reserved_terms:
            reserved_dict = get_reserved_pricing(terms)
            writeReserved(reserved_dict, regionsDict[location], sku, instanceType, operatingSystem, preInstalledSw, test_writer)

    s3.meta.client.upload_file( "/tmp/" + filename, os.environ['s3_bucket'], "Services/" + "EC2/" + filename)
    os.remove("/tmp/" + filename)

def rds_servicecode(servicecode,region):
    client = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.resource('s3')
    #now = datetime.datetime.now()

    response = client.get_products(
        ServiceCode='AmazonRDS',
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

    filename = regionsDict.get(region) + "_" + servicecode + ".csv"
    test_file = open("/tmp/" + filename, mode='w')
    test_writer = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    test_writer.writerow(['Region', 'SKU', 'InstanceType', 'deploymentOption', 'Pricing' 'Plan', 'Hourly', 'Upfront'])

    for PRODUCT in response['PriceList']:
        mydict = json.loads(PRODUCT)
        product_name = mydict.get('product')
        if product_name.get('productFamily') not in ['Database Instance']:
            continue
        servicecode = mydict['product']['attributes']['servicecode']
        location = mydict['product']['attributes']['location']
        sku = mydict['product']['sku']
        instanceType = mydict['product']['attributes']['instanceType']
        deploymentOption = mydict['product']['attributes']['deploymentOption']
        terms = mydict.get('terms')
        ondemand_terms = terms.get('OnDemand',{})
        priceOnDemand = 0.0
        
        for ondemand_term in ondemand_terms:
            price_dimensions = ondemand_terms.get(ondemand_term).get('priceDimensions')
            for price_dimension in price_dimensions.keys():
                priceOnDemand = price_dimensions.get(price_dimension).get('pricePerUnit').get('USD')
        test_writer.writerow([regionsDict[location], sku, instanceType, deploymentOption.replace('-','_'), 'OnDemand' , str(priceOnDemand).rstrip('0').rstrip('.'), '0'])

        reserved_terms = terms.get('Reserved', {})
        if reserved_terms:
            reserved_dict = get_reserved_pricing(terms)
            writeReservedRDS(reserved_dict, regionsDict[location], sku, instanceType, deploymentOption, test_writer)

    s3.meta.client.upload_file( "/tmp/" + filename, os.environ['s3_bucket'], "Services/" + "RDS/" + filename)
    os.remove("/tmp/" + filename)

def handler(event, context):
    for region in regionsDict:
        ec2_servicecode("AmazonEC2",region)
        rds_servicecode("AmazonRDS", region)
    print ('Finished!')