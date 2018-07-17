import boto3
import zipfile
import StringIO
import mimetypes

s3 = boto3.resource('s3')

jeffdiers_bucket = s3.Bucket('jeffdiers.com')
build_bucket = s3.Bucket('build.jeffdiers.com')

build_zip = StringIO.StringIO()
build_bucket.download_fileobj('buildJeffdiers.zip', build_zip)

with zipfile.ZipFile(build_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        build_bucket.upload_fileobj(obj, nm, 
          ExtraArgs={'ContentType': str(mimetypes.guess_type(nm)[0])}
        )
        build_bucket.Object(nm).Acl().put(ACL='public-read')