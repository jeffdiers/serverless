import boto3
import boto3
import zipfile
import StringIO
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:849548794507:deploy_jeffdiers')

    location = {
      'bucketName': 'build.jeffdiers.com',
      'objectKey': 'buildJeffdiers.zip'
    }
    try:
        job = event.get('CodePipeline.job')

        if job:
          for artifact in job['data']['inputArtifacts']:
            if artifact['name'] == 'MyAppBuild':
              location = artifact['location']['s3Location']

        print 'Building from ' + str(location)
        s3 = boto3.resource('s3')
        
        jeffdiers_bucket = s3.Bucket('jeffdiers.com')
        build_bucket = s3.Bucket(location['bucketName'])
        
        build_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location['objectKey'], build_zip)
        
        with zipfile.ZipFile(build_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                jeffdiers_bucket.upload_fileobj(obj, nm, 
                  ExtraArgs={'ContentType': str(mimetypes.guess_type(nm)[0])})
                jeffdiers_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print 'Done!' 
        topic.publish(Subject="Jeffdiers.com deploy", Message="it deployed, cunt")
        if job:
          codepipeline = boto3.client('codepipeline')
          codepipeline.put_job_success_result(jobId=job['id'])
    except:
        topic.publish(Subject="Jeffdiers.com deploy", Message="didn't deploy, cunt")
        raise       
            
    return 'Built project'
