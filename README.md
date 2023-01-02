# Dependaware
### A github action that helps to send your Dependabot Alerts to Slack and Linear for Critical and High issues (PS: More integrations to be added).
---

Using Dependaware in your workflow is very easy , copy the example  workflow file and replace all the required tokens and values . Make sure to schedule the run  for every  7 days , as the action only alerts for new vulnerabilites that have occured in the last 7 days . This is done in order to prevent the action from creating duplicate tickets in Linear for the same vulnerabilites over and over. 



Required Inputs

```
github_personal_token:
    description: " Github Personal Token to Query github for dependabot alerts"
    required: true
  slack_token:
    description: " Slack Bot Token to Send Alerts "
    required: true
  channel:
    description: " Slack Channel to Send the Alerts Too"
    required: true
  linear_api_key:
    description: " Token Required for querying Linear GraphQL API"
    required: true
  linear_team_id:
    description: " Your Organizations Team ID to create issues for"
    required: true
```


          
The Action also provides ouptuts that can be further used in your workflows for geting the stats as summaries , perform conditional logic with the stats of these alerts 

```
outputs:
  total_alerts:
    description: "Total Open Alerts"
  critical_alerts:
    description: "Open Critical Alerts"
  high_alerts:
    description: "Open High Alertss"
  moderate_alerts:
    description: "Open Moderate Alerts"
  low_alerts:
    description: "Open Lower Alerts"
```
          
 Workflow File Example
 
 
``` name: Dependaware
on:
  schedule:
    - cron: "0 0 * * 1"
  workflow_dispatch:

jobs:
  send-slack-alerts:
    runs-on: ubuntu-latest
    steps:
      - name: Dependaware
        id: aware
        uses: alvacoder/Dependaware@v1.0
        with:
          github_personal_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          slack_token: ${{ secrets.SLACK_TOKEN }}
          channel: CHWEX34534
          linear_api_key: ${{ secrets.LINEAR_API_KEY }}
          linear_team_id: '434KJLX-J'
    
    - name: Check Ouptuts
        run: |
          echo ${{ steps.aware.outputs.total_alerts }} 
 ```
 
          
 
