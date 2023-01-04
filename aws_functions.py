import boto3, itertools

def upload(file_name, bucket, object_name):
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def download(file_name, bucket):
    s3 = boto3.resource('s3')
    output = f"download_files/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)
    return output

##################### keep this    
def list_all_files(bucket):
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)
    return contents

def list_slum_admins():
    ec2 = boto3.client('ec2', 'us-east-1')
    admins = []
    filters = [
        {
            'Name': 'instance-state-name', 
            'Values': ['running', 'stopped']
        },
        {
            'Name': 'tag:slumbering-admin', 
            'Values': ['true']  
        }
    ]
    msg_running=[]
    msg_stopped=[]
    reservations = ec2.describe_instances(Filters=filters).get('Reservations', [])
    for reservation in reservations:
        for instance in reservation['Instances']:
            tags = {}
            for tag in instance['Tags']:
                tags[tag['Key']] = tag['Value']
                if tag['Key'] == 'Name':
                    name=tag['Value']
                
                    admins.append(name)
                    print(admins)
                    return admins 
        # dynamodb = boto3.client('dynamodb', 'us-east-1')
        # response = dynamodb.scan(TableName='')
        # data = response['Items']
        # while 'LastEvaluatedKey' in response:
        #     response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        #     data.extend(response['Items'])
        # return data

