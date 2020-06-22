import zipfile
import os
import sys
import boto3
import json

def config():
    with open('./conf.json') as json_file:
        data = json.load(json_file)
    return data

session = boto3.Session()
conf = config()

def main():
    try:
        print("\nLambda sendo compactado...")
        zip_path = zip_lambda()
        print("Lambda compactado em "+zip_path+".")
        paths = [zip_path,"./libs/elasticsearch.zip","./libs/google-language-api.zip","./libs/grabzit.zip","./libs/hashlib.zip"]
        for file in paths:
           print("Enviando "+file+"...")
           responseS3 = send_s3(file)
           print(file+" enviado com sucesso para "+conf['bucket_name']+".")
        os.remove(zip_path)
        responseCF = create_stack()
        if responseCF['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("STACK INICIADA COM SUCESSO\n")
            print(responseCF)
        else:
            print("STACK COM PROBLEMAS\n")
            print(responseCF)
    except Exception as e:
        raise e


def zip_lambda():
    file_paths = ['./lambda_function.py',conf['google_credentials_path']]
    for file_name in file_paths: 
        with zipfile.ZipFile('lambda_lgbtqia.zip','w') as zip:
            for file in file_paths:
                zip.write(file, arcname=os.path.basename(file))
            zip_path = zip.filename
    return zip_path

def send_s3(file_path):
    s3_client = session.client('s3')
    response = s3_client.upload_file(file_path, conf['bucket_name'],"lgbtqia/"+os.path.basename(file_path))
    return response

def parse_template(template):
    cf = session.client('cloudformation')
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    cf.validate_template(TemplateBody=template_data)
    return template_data

def create_stack():
    cf = session.client('cloudformation')
    response = cf.create_stack(
        StackName="lgbtqia-helper-stack",
        TemplateBody=parse_template('./stack.json'),
        Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND'],
        Parameters= [
        {
            "ParameterKey": "S3Bucket",
            "ParameterValue": conf['bucket_name']
        },
        {
            "ParameterKey": "ClusterSecurityGroup",
            "ParameterValue": conf['cluster_elastic']['security_group']
        },
        {
            "ParameterKey": "ClusterSubnetId",
            "ParameterValue": conf['cluster_elastic']['subnet']
        },
        {
            "ParameterKey": "LambdaSecurityGroup",
            "ParameterValue": conf['lambda']['security_group']
        },
        {
            "ParameterKey": "LambdaSubnetIds",
            "ParameterValue": conf['lambda']['subnet']
        },
        {
            "ParameterKey": "TwitterConsumerKey",
            "ParameterValue": conf['twitter']['consumer_key']
        },
        {
            "ParameterKey": "TwitterConsumerSecret",
            "ParameterValue": conf['twitter']['consumer_secret']
        },
        {
            "ParameterKey": "TwitterOAuthToken",
            "ParameterValue": conf['twitter']['oauth_token']
        },
        {
            "ParameterKey": "TwitterOAuthTokenSecret",
            "ParameterValue": conf['twitter']['oauth_secret']
        },
        {
            "ParameterKey": "KeyPair",
            "ParameterValue": conf['key_pair_name']
        }
        ])
    return response

if __name__ == "__main__": 
    main()