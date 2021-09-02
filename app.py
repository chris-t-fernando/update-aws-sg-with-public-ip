from requests import get
import boto3

ip = get("https://api.ipify.org").text + "/32"

ec2Client = boto3.client("ec2")

describe_response = ec2Client.describe_security_group_rules(
    Filters=[
        {
            "Name": "group-id",
            "Values": [
                "sg-8b5c50ee",
            ],
        },
    ],
)


for r in describe_response["SecurityGroupRules"]:
    stale_rule = False
    for t in r["Tags"]:
        if t["Key"] == "home-ip" and t["Value"].lower() == "true":
            # found an existing SG entry. Now check if it is for my IP
            if r["CidrIpv4"] != ip:
                # my IP has changed since last run - need to delete this rule and re-create it
                stale_rule = True
                print(f"Found stale rule - {r['CidrIpv4']}")
                break

    if stale_rule:
        # delete the old rule
        try:
            delete_response = ec2Client.revoke_security_group_ingress(
                GroupId="sg-8b5c50ee",
                SecurityGroupRuleIds=[
                    r["SecurityGroupRuleId"],
                ],
            )
            print(f"Successfully deleted stale rule ID {r['SecurityGroupRuleId']}")
        except Exception as e:
            print(
                f"Failed to delete stale rule ID {r['SecurityGroupRuleId']}.  Error: {str(e)}"
            )
            exit()

        # create the new rule
        try:
            create_response = ec2Client.authorize_security_group_ingress(
                GroupId="sg-8b5c50ee",
                IpPermissions=[
                    {
                        "FromPort": r["FromPort"],
                        "ToPort": r["ToPort"],
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {
                                "CidrIp": ip,
                                "Description": "Access from home network",
                            },
                        ],
                    },
                ],
            )
            print(f"Set {r['FromPort']} rule succesfully.")

        except Exception as e:
            print("error")
            if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
                print(f"Unable to set {r['FromPort']} rule. Error: {str(e)}")
