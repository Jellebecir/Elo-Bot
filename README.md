# Elo-Bot
Slack bot used to keep track of 2 player games with a binary outcome and gives a rating based on the elo system.

# Setup
How to setup the development environment of Elo-Bot

## Setting development mode
before running the server, make sure to use `setx DEVELOPMENT true`. This tells the bot to use different environment variables.

## Starting test server
[NGROK](https://ngrok.com/) is required to respond to events (slack events and bot commands). If not already installed click the provided link to the NGROK website.

Once this is installed, run bot.py. In the terminal you will see on which port the Flask server is running. For development it will probably say something along the lines of http://127.0.0.1:5000, meaning it's running on port 5000.

Now run the ngrok.exe file and type `ngrok http 5000`. In the terminal, it will say that it's forwarding an ngrok adress to your local flask server. Copy this ngrok adress, go to the event subscription tab of the [slack app webpage](https://api.slack.com/apps), and paste it in the request url appended with `/slack/events` e.g. `https://16ea-82-174-48-158.ngrok-free.app/slack/events`.

It's important to note that when the ngrok server needs to be reset, you'll receive a different forwarding adress and it needs to be set again in the slack app page.

