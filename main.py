import boto3
from datetime import datetime, timedelta
import time
import json
from io import BytesIO


session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key=''
)

lambda_client = session.client('lambda',region_name='us-east-1')
s3 = session.client('s3', region_name='us-east-1')

bucket_name = ''

params = {
    'Bucket': bucket_name,
    'MaxKeys': 1000
}


output_bucket_name = ''
outputparams = {
    'Bucket': output_bucket_name,
    'MaxKeys': 1000
}
output_objects = set()
updated_objects = set()
while True:
    tmp = set()
    response = s3.list_objects_v2(**params)
    for obj in response.get('Contents', []):
        tmp.add(obj['Key'])
    updated_objects_ref = tmp-updated_objects
    print("Number of object added: ",len(updated_objects_ref))

    for i in updated_objects_ref:
        input_data = {
            "Records": [{"s3":{"bucket":{"name":bucket_name},"object":{"key":i}}}]
        }
        payload = json.dumps(input_data)
        #print("Invoked",i,datetime.now())
        response = lambda_client.invoke(
            FunctionName='',
            InvocationType='Event',
            Payload=payload
        )
        #print("Finished",i,datetime.now())

    updated_objects=tmp.copy()
    
        
    #loading output
    output_response = s3.list_objects_v2(**outputparams)
    tmp = set()
    for obj in output_response.get('Contents', []):
        tmp.add(obj['Key'])
    output_objects_ref = tmp-output_objects #output objects not downloaded

    with open('output.txt','a') as f:
        for i in output_objects_ref:
            obj = s3.get_object(Bucket=output_bucket_name,Key=i)
            fc = obj['Body'].read().decode('utf-8')
            print(i+","+fc)
            f.write(i+","+fc+"\n")
    output_objects = tmp.copy()
    
    
    time.sleep(10)

print("Exit")
