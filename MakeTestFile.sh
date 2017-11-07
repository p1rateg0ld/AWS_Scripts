#!/bin/bash -x

INSTANCEID="i-594c6bc3"
SCRIPTPATH="C:\/Users\/Administrator\/Documents\/Powershell-Scripts\/MakeTestFile.ps1"
TIMEOUT="600"
REGION="us-east-1"
PROFILE="josh"

JSON="{\"commands\":[\"${SCRIPTPATH}\"]}"


aws ssm send-command --document-name "AWS-RunPowerShellScript" --instance-ids $INSTANCEID --parameters $JSON --timeout-seconds $TIMEOUT --region $REGION --profile $PROFILE
