# Dependalinear
### A github action that helps to send your Dependabot Alerts to Slack, Linear and create JIRA Tickets for Critical and High issues.
---

Using Dependalinear in your workflow is very easy , copy the example  workflow file and replace all the required tokens and values . Make sure to schedule the run  for every  7 days , as the action only alerts for new vulnerabilites that have occured in the last 7 days . This is done in order to prevent the action from creating duplicate tickets in JIRA for the same vulnerabilites over and over. 



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
  jira_token:
    description: " Token Required for quering JIRA REST API"
    required: true
  jira_url:
    description: " Your Organizations Jira Cloud URL"
    required: true
  jira_useremail:
    description: " Email id of the user associated with the token"
    required: true
  jira_project_key:
    description: " The Project Key for which Jira Tickets are created "
    required: true
  jira_issue_type:
    description: " Issue Type As Task or Epic or INC"
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
 
 
``` name: Dependalinear
on:
  schedule:
    - cron: "0 0 * * 1"
  workflow_dispatch:

jobs:
  send-slack-alerts:
    runs-on: ubuntu-latest
    steps:
      - name: Dependalinear
        id: linear
        uses: alvacoder/Dependalinear@v1.3
        with:
          github_personal_token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          slack_token: ${{ secrets.SLACK_TOKEN }}
          channel: CHWEX34534
          jira_token: ${{ secrets.JIRA_API_TOKEN }}
          jira_url: 'https://[companyy].atlassian.net'
          jira_useremail: 'abc@xyzcompany.com'
          jira_project_key: 'INC'
          jira_issue_type: 'Task'
    
    - name: Check Ouptuts
        run: |
          echo ${{ steps.linear.outputs.total_alerts }} 
 ```
 
          
 
