import datetime


servicecode = "AmazonEC2"
region = "EU (Ireland)"

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
    now = datetime.datetime.now()
    filename = regionsDict.get(region) + "_" + servicecode + "_" + now.strftime("%Y-%m-%d") + ".csv"
    print (filename)

if servicecode == "AmazonEC2":
    ec2_servicecode(servicecode, region)


