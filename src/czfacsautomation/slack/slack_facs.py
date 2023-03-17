from json import load
import logging
from pkg_resources import Requirement, resource_filename
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError, SlackRequestError


class SlackFacs:
    """Communicate with Slack App to notify users of current run status.
    """
    
    def __init__(self, location: str):
        """Setup the connection between the automation software and Slack channel
        
        :param location: the system location for each physical instrument
        :type location: str
        :raises FileNotFoundError: Logs critical if the Slack config file is not found
        """
        self.location = '{}{}'.format('autofacs', location)
        slack_config_file = resource_filename(Requirement.parse("czfacsautomation"),"../config/Slack_config.json")
        
        try:
            with open(slack_config_file, 'r') as f:
                self._slack_config = load(f)
                
        except FileNotFoundError:
            logging.critical('Config file not found')
        
        self.SLACK_BOT_TOKEN = self._slack_config['BOT_TOKEN'][self.location]
        self.client = WebClient(token=self.SLACK_BOT_TOKEN)
        self.channel = self._slack_config['Channel_ID'][self.location]
        self.timestamp = ""

    def userCheck(self, user) -> str:
        """Confirms that the user has a verified slack ID
        
        :param user: the entered name of the user
        :type user: str    
        :return: The user name
        :rtype: str
        """
        user = user.upper()
        return (user in self._slack_config['Member_ID'])
    
    def sendMessage(self, state, user):
        """Post a message in the specified Slack channel based on the progress of the FACS automation

        :param state: the state of the automation process for which to look up the message to post
        :type state: str
        :raises SlackApiError: If message cannot be posted
        :raises SlackRequestError: If Slack cannot connect
        :param user: the name of the user for which to mention in specific messages
        :type user: str
        :return: The timestamp signature of the parent Slack message for automation startup
        :rtype: str of the format '1234567890.012345']
        """        
        
        slack_message = self._slack_config[state]['message']
        contact = self._slack_config['Member_ID'][user]
        
        if state == 'FACS_complete' or state == 'FACS_pause':
            slack_message = f"{contact} {slack_message}"

        try:
            #link_names=True allows for @mentions, such as @channel
            response = self.client.chat_postMessage(channel = self.channel, link_names=True, text=slack_message)
            logging.critical(f"Slack Timestamp: {response['ts']}")
        
        except SlackApiError as e:
            logging.critical(f"SlackAPI Error: {e.response['error']}")
            
        except SlackRequestError as err:
            logging.critical(f"SlackRequest Error: {err.response['error']}")
        
        except Exception as error:
            logging.critical(f"Other Slack Error: {error}. Slack message did not post.")
            
        if state == 'FACS_startup':
           return(response["ts"])
            
    def tubeStatusThread(self, tube_no: int, timestamp, start = True):
        """Post a threaded message in the specified Slack channel with the current tube number progress
        
        :param tube_no: the current tube number
        :type tube_no: int
        :param timestamp: The timestamp signature of the parent Slack message for automation startup
        :type timestamp: str of the format '1234567890.012345'
        :param start: the status of a specific tube, either start or finish
        :type start: bool
        :raises SlackApiError: If message cannot be posted
        :raises SlackRequestError: If Slack cannot connect
        """       
        tube_no += 1
        
        if start:
           slack_message = f"Starting Tube {tube_no}"
        else:
           slack_message = f"Finished Tube {tube_no}"
        
        try:
            response = self.client.chat_postMessage(channel = self.channel, link_names= True, thread_ts = timestamp, text=slack_message)
            logging.critical(f"Threaded Slack Timestamp: {response['ts']}")
            
        except SlackApiError as e:
            logging.critical(f"SlackAPI Error: {e.response['error']}")
            
        except SlackRequestError as err:
            logging.critical(f"SlackRequest Error: {err.response['error']}")
        
        except Exception as error:
            logging.critical(f"Other Slack Error: {error}. Slack message did not post.")
        
    def uploadFile(self, filepath):
        """Upload files to the specified Slack channel
        
        :param filepath: the file to upload
        :type filepath: str
        :raises SlackApiError: If file cannot be uploaded
        :raises SlackRequestError: If Slack cannot connect
        """
        
        try:
            response = self.client.files_upload(file = filepath)
            fileLink = response['file']['permalink']
            logging.critical(f"Uploaded file: {filepath} to Slack at {fileLink}")
            
        except SlackApiError as e:
            logging.critical(f"SlackAPI Error: {e.response['error']}")
            
        except SlackRequestError as err:
            logging.critical(f"SlackRequest Error: {err.response['error']}")
        
        except Exception as error:
            logging.critical(f"Other Slack Error: {error}. Slack message did not post.")
            
        try:    
            msg = "Automation Paused or Stopped. Here is the screen shot:"
            msg = msg + "<{}| >".format(fileLink)
            posting = self.client.chat_postMessage(channel = self.channel, text = msg)
            logging.critical(f"Posted file: {filepath}")
        
        except SlackApiError as e:
            logging.critical(f"SlackAPI Error: {e.response['error']}")
            
        except SlackRequestError as err:
            logging.critical(f"SlackRequest Error: {err.response['error']}")
        
        except Exception as error:
            logging.critical(f"Other Slack Error: {error}. Slack message did not post.")
    
    def deleteMessage(self, timestamp):
        """Delete a specific message in the specified Slack channel 

        :param timestamp: The timestamp signature of the message to be deleted
        :type timestamp: str of the format '1234567890.012345'
        :raises SlackApiError: If message cannot be deleted
        :raises SlackRequestError: If Slack cannot connect
        """               
        
        try:
            response = self.client.chat_delete(channel = self.channel, ts = timestamp)
            logging.critical(f"Deleted Slack Timestamp: {response['ts']}")
            
        except SlackApiError as e:
            logging.critical(f"SlackAPI Error: {e.response['error']}")
        
        except SlackRequestError as err:
            logging.critical(f"SlackRequest Error: {err.response['error']}")
        
        except Exception as error:
            logging.critical(f"Other Slack Error: {error}. Slack message did not post.")