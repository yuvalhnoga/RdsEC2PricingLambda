# Cloudformation yaml for AWS pricing for EC2 and RDS

### index.py.zip
The lambda function in a zip file used for the cloudformation.

### pricingCFN.yaml
Cloudformation yaml that creates: 
- Lambda
- Glue crawler + database
- Cloudwatch event that will run the lambda daily
- Roles for them

### Instructions for deployment.
- Create a S3 bucket and insert the **index.py.zip** to that bucket.
- Create a stack and upload the **pricingCFN.yaml**
- Enter the newly created S3 bucket name.
- You will need to manually run the Lambda and Crawler.
- Lambda will run **daily** by cloudwatch event.
- Have fun