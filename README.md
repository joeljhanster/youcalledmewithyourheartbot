# youcalledmewithyourheartbot
This repository is mainly for the development of a Telegram bot that I have made to ask a very special girl in my life to be my girlfriend. Just trying my best to learn new things and apply them to my own personal life!

### Commands
`/start`: By starting the bot, it means that the girl you have been chasing has finally said YES!<br/>
`/write`: Support each other with a word of encouragement!<br/>
`/journal`: Store our favourite photos and caption it! Let's keep our memories!<br/>
`/viewjournal`: Let's visit memory lane!<br/>
`/date`: Make dating fun with wild ideas!<br/>

### Functionalities
1. `/write`
- This command allows you to write a message to your partner!
- Sometimes, it is always nice to hear a word of encouragement from your partner! Even more so, when it comes as a surprise!
<p align=center><img src="https://github.com/joeljhanster/youcalledmewithyourheartbot/blob/master/write.png" width=50% /></p>

2. `/journal`
- This command involves the use of Google and Blogger API because any updates will be translated into a Blogger post!
- This process comes in 3 phases: 1) Upload a photo 2) Insert a title 3) Write a caption

3. `/viewjournal`
- This command tells you where you can find all the Blogger posts created from `/journal` command!
- In essence, this provides the Blogger URL!
<p align=center>
<img src="https://github.com/joeljhanster/youcalledmewithyourheartbot/blob/master/journal1.png" width=30%/>
<img src="https://github.com/joeljhanster/youcalledmewithyourheartbot/blob/master/journal2.png" width=30%/>
</p>

4. `/date`
- This command uses a random generator to select a dating idea from a list created in Google Docs!
- Using the Telegram Keyboard Markup, 4 categories are created (namely Adventure, Chill, Overseas, Learning)
- Each category will reference a different Google Docs file and it will randomly select a sentence using the `select_sentence(document, messageType)` function. More information about this function can be found below.

5. Daily Encouragement
- Using Telegram's Job Queue, the bot will send an encouragement message every day at a special timing!
- This uses the `select_sentence(document, messageType)` function as well.

6. Special Day
- The bot will also check if it is a special day, e.g. Birthdays, Anniversary, Valentine's Day etc.
- At 12am, it will send a lovely personalised message! Followed by a GIF that uses `select_sentence(document, messageType)` function too!

### Code
`select_sentence(document, messageType)`
- This function makes use of the Google Docs API to randomly select a sentence that is created in the Google Docs file.
- Using the `googledoc.py` file, the Google Docs files are first created using my Google Account.
- Subsequently, I will head over to my Google Drive to retrieve the ID.
- To distinguish a sentence, I will add each line to form the sentence until the line is an empty line. This sentence will then be appended into the `sentence_lst` list if it is not in the list stated in the `used` dictionary.
- Using a random generator, I then randomly select a sentence from `sentence_lst` and that is my output for the function.

### Heroku App
To ensure that the Telegram bot is persistently running 24/7, it is currently hosted on Heroku App with one worker running.

##### NOTE: This is a self-initiated project that is used for me to chase the girl of my dreams and for us to explore life together in a unique and interesting way! I will not disclose the blog and telegram bot details! Even you manage to access the telegram bot, you will be told that "You do not belong here!"
