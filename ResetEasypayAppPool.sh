#!/bin/bash -x

INSTANCEID="i-d66b4c4c"
SCRIPTPATH="C:\/Users\/Administrator\/Documents\/Powershell-Scripts\/EasypayAppPoolReset.ps1"
TIMEOUT="600"
REGION="us-east-1"
PROFILE="josh"

JSON="{\"commands\":[\"${SCRIPTPATH}\"]}"


aws ssm send-command --document-name "AWS-RunPowerShellScript" --instance-ids $INSTANCEID --parameters $JSON --timeout-seconds $TIMEOUT --region $REGION --profile $PROFILE
