"""
 * @author Idris Adeniji (alvacoder)
 * @email idrisadeniji01@gmail.com
 * @create date 2022-12-28 17:41:56
"""

import requests
import os 
import sys
import json
import datetime
from dateutil import parser
from jira import JIRA
#implement grepping dependabot alerts through graphql
class Dependalinear(object):

    def __init__(self):


        # Required Secrets for this awesome code to function.
        self.github_token=os.environ["INPUT_GITHUB_PERSONAL_TOKEN"]

        # Required Jira Variables 
        self.jira_token=os.environ["INPUT_JIRA_TOKEN"]
        self.jira_url=os.environ["INPUT_JIRA_URL"]
        self.jira_useremail=os.environ["INPUT_JIRA_USEREMAIL"]
        self.jira_projectKey=os.environ["INPUT_JIRA_PROJECT_KEY"]
        self.jira_issue_type=os.environ["INPUT_JIRA_ISSUE_TYPE"]
        # Required Slack Variables 
        self.slack_token=os.environ["INPUT_SLACK_TOKEN"]
        self.slack_channel=os.environ["INPUT_CHANNEL"]
        # Initilializing required Varibales for this code
        self.alerts={}
        self.total_alerts=0
        self.stats={"CRITICAL":0,"HIGH":0,"MODERATE":0,"LOW":0}
        self.reponame=os.environ["GITHUB_REPOSITORY"].split("/")[-1]
        self.owner=os.environ["GITHUB_REPOSITORY_OWNER"]
        self.dependabot_url="https://github.com/{}/{}/security/dependabot".format(self.owner,self.reponame)

    
    def fetch_alerts(self):
        
        query= """
        {
            repository(name: "REPO_NAME", owner: "REPO_OWNER") {
                vulnerabilityAlerts(first: 100 states: OPEN) {
                    nodes {
                        createdAt
                        dismissedAt
                        securityVulnerability {
                            severity
                            package {
                                name
                            }
                            advisory {
                                 summary
                                 ghsaId
                                 permalink
                            }
                            
                        }
                    }
                }
            }
        }  """
        query=query.replace("REPO_NAME",self.reponame)
        query=query.replace("REPO_OWNER",self.owner)
        
        # Github Api to fetch the required data 
        
        url="https://api.github.com/graphql"
        header= { "Authorization":"Bearer {}".format(self.github_token)}
        response=requests.post(url,headers=header,json={'query':query})
        print(response.text)

        # Check Response 
        if response.status_code==200:
            data=response.text
            data_dict=json.loads(data)
            return data_dict
        else :
            print(response.reason)
            sys.exit(1)

    
    def parse_data(self):

        data_dict=self.fetch_alerts()
        if data_dict["data"]["repository"]["vulnerabilityAlerts"]["nodes"]:
            for nodes in data_dict["data"]["repository"]["vulnerabilityAlerts"]["nodes"]:
                
                # Store data as {"ghsaid":["severity","advisory","advisory_url",""]}
                created_at=nodes["createdAt"]
                package_name=nodes["securityVulnerability"]["package"]["name"]
                severity=nodes["securityVulnerability"]["severity"]
                advisory=nodes["securityVulnerability"]["advisory"]["summary"]
                ghsaid=nodes["securityVulnerability"]["advisory"]["ghsaId"]
                advisory_url=nodes["securityVulnerability"]["advisory"]["permalink"]

                #Create Alert Dictionary
                if not ghsaid in self.alerts.keys():
                    self.alerts[ghsaid]=[severity,advisory,advisory_url,created_at,package_name]
            
                
                # Calculating frequnecy of Each Alerts
                self.stats[severity]+=1 
            for keys in self.stats.keys():
                    self.total_alerts+=self.stats[keys] 
                
        else:
            print("no Vulnerabilites")
            sys.exit(0)
    
    def filter_new_alerts(self):

        """ This method helps to filter only the alerts that are created only within 7 Days """
       
        self.filtered_alerts={}
        self.parse_data()
        for ele in self.alerts:
            created_at=self.alerts[ele][3]
            date_formated=parser.parse(created_at)
            date_as_list=str(date_formated).split(" ")[0].split("-")
            converted_date=datetime.date(int(date_as_list[0]),int(date_as_list[1]),int(date_as_list[2]))
            today_date=datetime.date.today()
            date_diff_as_str=str(abs(converted_date - today_date))
            date_diff_as_number=int(date_diff_as_str.split(",")[0].split(" ")[0].split(":")[0])
            
            if date_diff_as_number <= 7:
                self.filtered_alerts[ele]=self.alerts[ele]

    def send_slack_alert(self):
        self.filter_new_alerts()
        url="https://slack.com/api/chat.postMessage"
        header={"Authorization":"Bearer {}".format(self.slack_token)}
        blocks=[]
        if bool(self.filtered_alerts):
            for key in self.filtered_alerts:
                block= {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Package Name:*\n{}".format(self.filtered_alerts[key][4])
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Severity:*\n{}".format(self.filtered_alerts[key][0])
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Summary:*\n{}".format(self.filtered_alerts[key][1])
                                }
                            ],
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Advisory",
                                
                                },
                                "value": "advisory",
                                "url":self.filtered_alerts[key][2],
                                "action_id": "button-action"
                            }
                            
                        }
                blocks.append(block)
            
            
            header_block={
                    "channel":self.slack_channel,
                        
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "*Dependabot Alerts for repo:* {}".format(self.reponame)
                                }
                                
                            },
                            {
                                "type": "divider"
                            },
                        ]

            }
            header_response=requests.post(url,json=header_block,headers=header)
            data={
                        "channel":self.slack_channel,
                        "blocks": blocks
                }
            content_response=requests.post(url,json=data,headers=header)


            if (json.loads(content_response.text)["ok"])==True and content_response.status_code==200:
                print("Slack Alert sent Successfully")
            else:
                print("Error Sending Slack Alert")
                print(content_response.text)
                sys.exit(1)
        else:
            print(" Skipping Slack and Jira Alerts ,No New Alerts for this week")
            sys.exit(0)
    
    def create_jira_issues(self):
        issue_list=[]
        try:

            jira=JIRA(self.jira_url,basic_auth=(self.jira_useremail,self.jira_token))

            description="Affected Package:{}\nRepo URL:{}\nAdvisory URL:{}\nDescription: {}\n"


            for key in self.filtered_alerts:
                if self.filtered_alerts[key][0]=="CRITICAL" or self.filtered_alerts[key][0]=="HIGH":
                    issue_details={
                            'project':self.jira_projectKey,
                            'summary': "Dependabot Alerts in repo : {}".format(self.reponame),
                            'description':description.format(self.filtered_alerts[key][4],self.dependabot_url,self.filtered_alerts[key][2],self.filtered_alerts[key][1]),
                            'issuetype': {'name': self.jira_issue_type},
                        }
                    issue_list.append(issue_details)
                    flag=True
                else:
                    flag=False
            if flag:
                issues=jira.create_issues(field_list=issue_list)
                print(" Jira Tickets Created for High and Critical Bugs")
            else:
                print("Jira Tickets Not Created ,there are no High or Critical Bugs This week")
                    
        except Exception as E:
            print("Exception occured :{}".format(E))
            sys.exit(1)
   
    def run(self):
        try:
            self.send_slack_alert()
            self.create_jira_issues()

            #set outputs
            print("::set-output name=total_alerts::{}".format(self.total_alerts))
            print("::set-output name=critical_alerts::{}".format(self.stats["CRITICAL"]))
            print("::set-output name=high_alerts::{}".format(self.stats["HIGH"]))
            print("::set-output name=moderate_alerts::{}".format(self.stats["MODERATE"]))
            print("::set-output name=low_alerts::{}".format(self.stats["LOW"]))
        except Exception as e:
            print("Exception:{}".format(e))
            sys.exit(1)


Dependalinear().run()


