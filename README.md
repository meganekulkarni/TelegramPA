Development coming soon

#Getting Started

________________

##API Setup

1. sign into telegram
2. message the botfather
3. run /newbot
4. follow the prompts to create a bot
5. Copy the API token


##Running the code

__________________

1. clone this repository
2. navigate to TelegramPA
3. pip install -r requirements.txt
4. run echo "TELEGRAMPA_PROJECT_HOME={pwd} \n TELEGRAM=YOUR_API_KEY"


###Run the telegram listener 

1. tmux new -s my-telegram-listener
2. in the tmux session run python3 telegram_listener.py
3. exit the tmux session by hitting <ctrl b> + <d>


###run the dash app

1. cd dash_app/
2. export FLASK_APP=main.py
3. FLASK run


