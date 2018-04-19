#!/usr/bin/env python3

from pprint import pprint
from Crypto.Cipher import AES
import boto3, pymysql, argparse
import os, base64
import pdb


def parse_arguments():
    parser = argparse.ArgumentParser(prog='aws-lookup', description="Multi purpose utility that pull data about ec2 instances from all regions accross multiple aws accounts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--scan", action='store_true', help="Scans all AWS accounts from DB")
    group.add_argument("-r", "--register", action='store_true', help="Checks if AWS account already registered or register the account.")
    group.add_argument("-d", "--delete", action='store_true', help="Delete AWS account and access keys from the database")
    group.add_argument("-l", "--list", action='store_true', help="Gives a list of all accounts registered")
    args = vars(parser.parse_args())
    return args

def MySqlInit(cur):
    cur._defer_warnings = True
    AWS_create_db = "CREATE DATABASE IF NOT EXISTS AWS;"
    cur.execute(AWS_create_db)
    cur.execute("use AWS;")
    LOS_CreateTable = "CREATE TABLE IF NOT EXISTS accounts (AccountId VARCHAR(64), AccessKey VARCHAR(128), Secret VARCHAR(128));"
    cur.execute(LOS_CreateTable)
    cur._defer_warnings = False


def CheckIfUserExists(TheAccountId,cur):
    FindUser = 'Select AccountId from accounts where AccountId="'+ TheAccountId + '";'
    CheckUserExists = cur.execute(FindUser)
    return CheckUserExists


def CreateUser(TheAccountId,cur):
    key = input("Enter ur key: ")
    secret = input("Enter ur secret: ")
    cipher = AES.new(Master_key,AES.MODE_ECB)
    encodedKey = base64.b64encode(cipher.encrypt(key.rjust(64)))
    encodedSecret = base64.b64encode(cipher.encrypt(secret.rjust(64)))
    query = "Insert into accounts values(\"%s\",\"%s\",\"%s\");" % (TheAccountId, encodedKey, encodedSecret)
    cur.execute(query)
    return "Completed"

def CheckIfzeroAccounts(cur):
    GetCount = 'Select * from accounts;'
    cur.execute(GetCount)
    rows = cur.fetchall()
    return len(rows)

def GetAccounts(cur):
    GetData = 'Select * from accounts;'
    cur.execute(GetData)
    rows = cur.fetchall()
    credbox = []
    for each_row in rows:
        account = each_row[0]
        key = each_row[1]
        secret = each_row[2]
        keystr = key.split("'")
        secretstr = secret.split("'")
        cipher = AES.new(Master_key,AES.MODE_ECB)
        access_key = cipher.decrypt(base64.b64decode(keystr[1].encode())).decode('utf-8').strip()
        secret_key = cipher.decrypt(base64.b64decode(secretstr[1].encode())).decode('utf-8').strip()
        credbottle = (account,access_key,secret_key)
        credbox.append(credbottle)
    return credbox

def DeleteAccount(cur):
    accid = input("Enter account to delete: ")
    GetAccid = 'Delete from accounts where AccountId=\"%s\"' % accid
    AccStatus = cur.execute(GetAccid)
    if AccStatus == 1:
        return "Account Deleted successfully"
    else:
        return "Failed to delete account. Does such account exist? "

def ViewAcc(cur):
    AllAcc = "Select AccountId from accounts;"
    cur.execute(AllAcc)
    Accdata = cur.fetchall()
    AccList = [x[0] for x in Accdata for y in x]
    return AccList

if __name__ == "__main__":
 
    args = parse_arguments()
    ### For Cosmetics
    rows, columns = os.popen('stty size', 'r').read().split()

    ### Code begins
    Master_key =  'MoveToVaultLater8394580183429013'
    MYSQL_SERVER = "172.17.0.6"
    MYSQL_PASSWORD = "mypassword"
    MYSQL_USER = "root"
    try:
        conn = pymysql.connect(host=MYSQL_SERVER, user=MYSQL_USER, passwd=MYSQL_PASSWORD, autocommit=True, charset='utf8')
        cur = conn.cursor()
        MySqlInit(cur)
    except:
        print("Error connecting MYSQL/MARIADB....")
        exit(2)

    if (args['register'] == True):
        TheAccountId = input("Enter your AWS Account id: ")
        Usercount = CheckIfUserExists(TheAccountId,cur)
        if (Usercount != 0):
            result_set = list(cur.fetchall()[0])
            result = result_set[0]
            if result == TheAccountId:
                print("User exists")
                cur.close();
                conn.close();
        else:
            Status = CreateUser(TheAccountId,cur)
            if Status == "Completed":
                print("AWS account registered successfully for monitoring")
            else:
                print("Error Occurred while performing user registration")

    elif args['scan'] == True:
        AccountCount = CheckIfzeroAccounts(cur)
        if AccountCount == 0:
            print("No Accounts to scan inside database. Please Register Accounts.")
            exit(0)
        Data_Session = boto3.session.Session()
        Regions = Data_Session.get_available_regions('ec2')
        AwsAccounts = GetAccounts(cur)

        for each_account in AwsAccounts:
            #pdb.set_trace()
            AccountId = each_account[0]
            AccessKey = each_account[1]
            AccessSecret = each_account[2]
            try:
                testclient = boto3.client("ec2",aws_access_key_id=AccessKey,aws_secret_access_key=AccessSecret,region_name="us-east-2")
                InstanceDetails = testclient.describe_instances()
            except:
                print("="*int(columns))
                print("The was a connection error for Account " + AccountId + " with his given keys.Kindly delete the user from database and reregister him with new keys ")
                print("="*int(columns))
                continue
            for RegionName in Regions[-2:]:
                client = boto3.client("ec2",aws_access_key_id=AccessKey,aws_secret_access_key=AccessSecret,region_name=RegionName)
                print("="*int(columns))
                print("Region: " + RegionName)
                print("Account: " + AccountId)
                InstanceDetails = client.describe_instances()
                if (InstanceDetails['Reservations'] == []):
                    print("0 instances found in " + RegionName)
                else:
                    for each_reserved in InstanceDetails['Reservations']:
                        for each1 in each_reserved['Instances']:
                            InstanceType = each1['InstanceType']
                            AvailabilityZone = each1['Placement']['AvailabilityZone']
                            for data in each1['Tags']:
                                if data['Key'] == 'Name':
                                    InstanceName = data['Value']
                                    print("Instance Name: " + InstanceName + "\nInstance Type: " + InstanceType + "\nAvailability Zone: " + AvailabilityZone )
    elif (args['delete'] == True):
        DeleteStatus = DeleteAccount(cur)
        print(DeleteStatus)
    else:
        ViewList = ViewAcc(cur)
        if len(ViewList) != 0:
            print("="*int(columns))
            print("Printing List of Accounts Regitered..")
            print("="*int(columns))
            for Account in ViewList:
                print(Account)
        else:
            print("No registered accounts found")




