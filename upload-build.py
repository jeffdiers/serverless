import boto3
import boto3
import zipfile
import StringIO
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:849548794507:deploy_jeffdiers')
    
    try:
        s3 = boto3.resource('s3')
        
        jeffdiers_bucket = s3.Bucket('jeffdiers.com')
        build_bucket = s3.Bucket('build.jeffdiers.com')
        
        build_zip = StringIO.StringIO()
        build_bucket.download_fileobj('buildJeffdiers.zip', build_zip)
        
        with zipfile.ZipFile(build_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                build_bucket.upload_fileobj(obj, nm, 
                  ExtraArgs={'ContentType': str(mimetypes.guess_type(nm)[0])})
                build_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print 'Done!' 
        topic.publish(Subject="Jeffdiers.com deploy", Message="it deployed, cunt")
    except:
        topic.publish(Subject="Jeffdiers.com deploy", Message="didn't deploy, cunt")
        raise       
            
    return 'Built project'
