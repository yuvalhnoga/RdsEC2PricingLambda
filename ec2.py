import boto3
import json

client = boto3.client('pricing')
response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=[
        {
            'Field': 'ServiceCode',
            'Type': 'TERM_MATCH',
            'Value': 'AmazonEC2',
        },
        {
            'Field': 'instanceType',
            'Type': 'TERM_MATCH',
            'Value': 'm5.xlarge',
        },
	{
            'Field': 'location',
            'Type': 'TERM_MATCH',
            'Value': 'EU (Ireland)',
        },
    ],
)
# print (type(response))
# print (response['PriceList'][0])

for PRODUCT in response['PriceList']:
    mydict = json.loads(PRODUCT)
    print ('"' + mydict['product']['attributes']['servicecode'], end='",')
    print ('"' + mydict['product']['attributes']['location'], end='",')
    print ('"' + mydict['product']['sku'], end='",')
    print ('"' + mydict['product']['attributes']['instanceType'], end='",')
    print ('"' + mydict['product']['attributes']['operatingSystem'], end='",')
    print ('"' + mydict['product']['attributes']['preInstalledSw'], end='",')
    first = next(iter(mydict['terms']['OnDemand']))
    second = next(iter(mydict['terms']['OnDemand'][first]['priceDimensions']))
    print ('"' + mydict['terms']['OnDemand'][first]['priceDimensions'][second]['pricePerUnit']['USD'], end='",')
    print ('"' + mydict['terms']['OnDemand'][first]['priceDimensions'][second]['description'], end='"\n')
    




#aws pricing get-products --service-code AmazonEC2 --filters "Type=TERM_MATCH,Field=location,Value=EU (Ireland)" --region us-east-1 | jq -rc '.PriceList[]' | jq -r '[ .product.attributes.servicecode, .product.attributes.location, .product.sku, .product.attributes.instanceType, .product.attributes.operatingSystem, .product.attributes.preInstalledSw, .terms.OnDemand[].priceDimensions[].pricePerUnit.USD, .terms.OnDemand[].priceDimensions[].description] | @csv' | pbcopy
# poop = json.loads(response['PriceList'][0])
# print (poop['product']['attributes']['instanceType'])

# output = json.dumps(response)
# print(output)
