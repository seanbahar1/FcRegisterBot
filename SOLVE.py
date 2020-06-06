#-- libraries to help connect to the discord server and to the google sheets api
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import json
class getFcInfo:
    def __init__(self,scope, cred, nameOfTheSheetFile, channel_name):
        self.scope = scope
        self.cred = cred
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.cred, self.scope)
        self.client_google = gspread.authorize(self.creds)
        self.nameOfTheSheetFile = nameOfTheSheetFile
        self.fcSheetFile = self.client_google.open(self.nameOfTheSheetFile).sheet1
        self.ChannelName = channel_name
        with open("discordkey.JSON") as f:
            discordClientKey = json.load(f)["discordKey"]
            print(discordClientKey)
        self.discordClientKey = discordClientKey
        #-- start client
        self.client_discord = discord.Client()

    def getSheetContents(self):
        return self.fcSheetFile.get_all_records()

    def startConnectionToDiscord(self):
        self.client_discord.run(self.discordClientKey)

    def updateNameList_row1(self):
        listOfMembers = []
        #-- getting what is already in the first row
        row = self.fcSheetFile.row_values(1)
        for name in row:
            listOfMembers.append(name)
        for member in self.client_discord.get_all_members():
            memName = member.name + "#" + member.discriminator
            print(memName)
            if memName in row:
                pass
            else:
                listOfMembers.append(memName)
        pprint(listOfMembers)
        self.fcSheetFile.delete_row(1)
        self.fcSheetFile.insert_row(listOfMembers)

    def updateCol(self,nameOfUser, restOfTheMessage,msg):
        #-- example message: Jane Grande 1 x pc ShadowBringers Tank Dps
        formatMessage = {"ff14name":"",
                         "amountOfChars":0,
                         "altWorld":False,
                         "platform":"",
                         "arr":False,
                         "hw":False,
                         "sb":False,
                         "shb":False,
                         "lvl80DOl":False,
                         "lvl80DOH":False,
                         "lvl80TANK":False,
                         "lvl80HEALER":False,
                         "lvl80DPS":False}

        #-- checking the message with specific parameters to crteate the data that will be saved in google sheets
        for i, word in enumerate(restOfTheMessage.split(" ")):
            if i > 4:
                break
            else:
                if i == 0:
                    formatMessage["ff14name"] += word + " "
                if i == 1:
                    formatMessage["ff14name"] += word + ""
                if i == 2 and word.isdigit():
                    formatMessage["amountOfChars"] = int(word)
                if i == 3:
                    if word == "x":
                        formatMessage["altWorld"] = False
                    elif word == "v":
                         formatMessage["altWorld"] = "altWorld True"
                if i == 4:
                    if word.lower() == "pc":
                        formatMessage["platform"] = "pc"
                    elif word.lower() == "ps4":
                         formatMessage["platform"] = "ps4"

        #-- lowering the message to check the message without being case sensetive
        restOfTheMessage = restOfTheMessage.lower()

        #-- determining the newest expansion
        if "shadowbringer" in restOfTheMessage or " shb " in restOfTheMessage:
            formatMessage["shb"] = True
            formatMessage["sb"] = True
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "stormblood" in restOfTheMessage or " sb " in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = True
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "heavensward" in restOfTheMessage or " hw " in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = False
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "arealmreborn" in restOfTheMessage or " arr " in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = False
            formatMessage["hw"] = False
            formatMessage["arr"] = True

        #-- checking if they got a tank dps etc'
        if " tank " in restOfTheMessage:
            formatMessage["lvl80TANK"] = True
        if " dps " in restOfTheMessage:
            formatMessage["lvl80DPS"] = True
        if " healer " in restOfTheMessage:
            formatMessage["lvl80HEALER"] = True
        if "dol" in restOfTheMessage:
            formatMessage["lvl80DOL"] = True
        if "doh" in restOfTheMessage:
            formatMessage["lvl80DOH"] = True

        #-- updating col
            #-- index in the row of the named user
        memName = nameOfUser.name + "#" + nameOfUser.discriminator
        row = self.fcSheetFile.row_values(1)
        index = -1
        #determining how many duplicate we goona have and ignore alot and then insert the names
        for i in range(len(row)):
            if row[i] == memName:
                index = i+1
                break

        #-- updating
        listThatWillBePosted = [memName]
        for entry in formatMessage:
            if formatMessage[entry] == False:
                if entry == "altWorld":
                    listThatWillBePosted.append("altWorld false")
                pass
            else:
                if "lvl80" in entry or "arr" in entry or "hw" in entry or "shb" in entry or "sb" in entry:
                    listThatWillBePosted.append(entry)
                else:
                     listThatWillBePosted.append(formatMessage[entry])

        #-- appending extra spaces so we wont leave something if the data is to short
        for i in range(10):
            listThatWillBePosted.append("")
        try:
            for i in range(len(listThatWillBePosted)):
                self.fcSheetFile.update_cell(i+1,index,listThatWillBePosted[i])
        except:
                msg.channel.send("something went wrong")

#-- starting asn instance of the class with the data it needs
fcSheet = getFcInfo(["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
                     "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"],
                     "cre.JSON",
                     "main page",
                     "bot-test-channel")

#-- defining the bots commands and what to listen to in the discord
@fcSheet.client_discord.event
async def on_message(message):
    #-- just printing the message
    print(message.channel, message.author)
    print(message.content, "\n")

    #-- if the message if from self ignore
    if message.author == fcSheet.client_discord.user and message.channel != fcSheet.ChannelName:
        return

    # -- do not call it wont be able to send it
    if message.content.startswith("!getList"):
        #await message.channel.send(fcSheet.getSheetContents())
        pprint(fcSheet.getSheetContents())

    #-- updating names in the sheet page
    if message.content.startswith("!updateNames"):
        await message.channel.send("updating names")
        pprint(fcSheet.updateNameList_row1())

    #-- allowing people tyo update their data
    if message.content.startswith("!updateMe"):
        if message.content == "!updateMe":
            #-- means they send the command without the parameters
            await message.channel.send("please add all the neccessary parameters <@"+str(message.author.id)+">")
            return
        await message.channel.send("updating.. <@" + str(message.author.id) +">")
        restOfMessage = message.content.replace("!updateMe ", "")
        pprint(fcSheet.updateCol(message.author, restOfMessage, message))

    #-- badically this will post the message structure
    if message.content.startswith("!help"):
        await message.channel.send("message format is:")
        await message.channel.send("***___!updateMe (firstName) (lastName) (AmountOfCharacters) (ifYouGotACharOnADifferentServerOrDataCenter(x/v) ) (pc/ps4) (latestExpansionYouOwn(ShadowBringers/stormblood/heavensward/aRealReborn) ) (Tank or Dps or healer or doh or dol (type all that you got at 80, without '()' ) )___***")
        await message.channel.send("Example:")
        await message.channel.send("!updateMe Jane Grande 1 x pc ShadowBringers Tank Dps DoL healer DOH  \n :grinning: ")


@fcSheet.client_discord.event
async def on_ready():
    print("started")

#-- starting the discord bot and connecting to the discord chat
fcSheet.startConnectionToDiscord()

