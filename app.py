from requests import get
import boto3

ip = get("https://api.ipify.org").text + "/32"

ec2Client = boto3.client("ec2")

try:
    response = ec2Client.authorize_security_group_ingress(
        GroupId="sg-8b5c50ee",
        IpPermissions=[
            {
                "FromPort": 3306,
                "ToPort": 3306,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": ip,
                        "Description": "SSH access from home",
                    },
                ],
            },
        ],
    )
    print(f"Set 3306 rule succesfully.")

except Exception as e:
    if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
        print(f"Unable to set 3306 rule. Error: {str(e)}")

try:
    response = ec2Client.authorize_security_group_ingress(
        GroupId="sg-8b5c50ee",
        IpPermissions=[
            {
                "FromPort": 22,
                "ToPort": 22,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": ip,
                        "Description": "SSH access from home",
                    },
                ],
            },
        ],
    )

    print(f"Set 22 rule succesfully.")
except Exception as e:
    if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
        print(f"Unable to set 22 rule. Error: {str(e)}")
