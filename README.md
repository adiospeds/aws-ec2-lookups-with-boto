# aws-ec2-lookups-with-boto [alpha version]
This is small example utility create with boto3 that can be used to pull ec2 data from multiple aws accounts.

- Login to AWS Account:
  - First create a user is ur aws account.
  - The create a role called BotoEc2ReadOnly
  - Attach the Ec2ReadOnly Policy to this Role
  - Attach the role to the user.
  - Generate a access key and secret key for the user.



Deployment:

```bash

Clone the repo to your machine
git clone https://github.com/adiospeds/aws-ec2-lookups-with-boto.git awsapp && cd awsapp

#Goto ur shell to deploy the app and run below commands:
docker run --name mysql -p 127.0.0.1:3306:3306 -e MYSQL_ROOT_PASSWORD=mypassword -d mysql:5

cd awsapp && docker build --no-cache -t awsapp .
docker run -it --link mysql:mysql --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp awsapp ./aws-lookup.py -h
#The above commnd will display you help / description on how to use the app.


```
Usage:
```
#To register an aws account for scanning run(you can register multiple users):
docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp awsapp ./aws-lookup.py -r

#To scan all registered users run:
docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp awsapp ./aws-lookup.py -s

#For more utils checkout help section:
docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp awsapp ./aws-lookup.py -h
```

