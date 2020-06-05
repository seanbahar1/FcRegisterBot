#-- google docs api so i could name all those in the fc discord
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import json
class getFcInfo:
    def __init__(self,scope, cred, nameOfTheSheetFile):
        self.scope = scope
        self.cred = cred
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.cred, self.scope)
        self.client_google = gspread.authorize(self.creds)
        self.nameOfTheSheetFile = nameOfTheSheetFile
        self.fcSheetFile = self.client_google.open(self.nameOfTheSheetFile).sheet1
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
    def updateCol(self,nameOfUser, restOfTheMessage):
        #-- example message: Jane Grande 1 x pc ShadowBringers Tank Dps
        formatMessage = {"ff14name":"","amountOfChars":0,"altWorld":False,"platform":"","arr":False,
                         "hw":False,"sb":False,"shb":False, "lvl80DOl":False,"lvl80DOH":False,"lvl80TANK":False,"lvl80HEALER":False,"lvl80DPS":False}

        for i, word in enumerate(restOfTheMessage.split(" ")):
            if i > 4:
                break
            else:
                if i == 0:
                    formatMessage["ff14name"] += word + " "
                if i == 1:
                    formatMessage["ff14name"] += word + ""
                if i == 2:
                    formatMessage["amountOfChars"] = int(word)
                if i == 3:
                    if word == "x":
                        formatMessage["altWorld"] = False
                    elif word == "v":
                         formatMessage["altWorld"] = True
                if i == 4:
                    if word.lower() == "pc":
                        formatMessage["platform"] = "pc"
                    elif word.lower() == "ps4":
                         formatMessage["platform"] = "ps4"

        restOfTheMessage = restOfTheMessage.lower()
        if "shadowbringer" in restOfTheMessage:
            formatMessage["shb"] = True
            formatMessage["sb"] = True
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "stormblood" in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = True
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "heavensward" in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = False
            formatMessage["hw"] = True
            formatMessage["arr"] = True
        elif "arealmreborn" in restOfTheMessage:
            formatMessage["shb"] = False
            formatMessage["sb"] = False
            formatMessage["hw"] = False
            formatMessage["arr"] = True
        if "tank" in restOfTheMessage:
            formatMessage["lvl80TANK"] = True
        if "dps" in restOfTheMessage:
            formatMessage["lvl80DPS"] = True
        if "healer" in restOfTheMessage:
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
        for i in range(len(row)):
            if row[i] == memName:
                index = i+1
                break
        #-- updating
        listThatWillBePosted = [memName]
        for entry in formatMessage:
            if formatMessage[entry] == False:
                pass
            else:
                if "lvl80" in entry or "arr" in entry or "hw" in entry or "shb" in entry or "sb" in entry:
                    listThatWillBePosted.append(entry)
                else:
                     listThatWillBePosted.append(formatMessage[entry])
        print(listThatWillBePosted)
        for i in range(len(listThatWillBePosted)):
            self.fcSheetFile.update_cell(i+1,index,listThatWillBePosted[i])

fcSheet = getFcInfo(["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
                     "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"],
                     "cre.JSON",
                     "main page")


@fcSheet.client_discord.event
async def on_message(message):
    print(message.channel)
    print(message.author)
    print(message.content)
    if message.author == fcSheet.client_discord.user and  message.channel != "bot-test-channel":
        return
    # -- what to do with the bot
    if message.content.startswith("!getList"):
        await message.channel.send(fcSheet.getSheetContents())
        pprint(fcSheet.getSheetContents())
    if message.content.startswith("!updateNames"):
        await message.channel.send("updating names")
        pprint(fcSheet.updateNameList_row1())
    if message.content.startswith("!updateMe"):
        await message.channel.send("updating.. starting updating PHASE <@" + str(message.author.id) +">")
        restOfMessage = message.content.replace("!updateMe ","")
        pprint(fcSheet.updateCol(message.author, restOfMessage))
    if message.content.startswith("!help"):
        await message.channel.send("message format is:")
        await message.channel.send("***___!updateMe (firstName) (lastName) (AmountOfCharacters) (ifYouGotACharOnADifferentServerOrDataCenter(x/v) ) (pc/ps4) (latestExpansionYouOwn(ShadowBringers/stormblood/heavensward/aRealReborn) ) (Tank or Dps or healer or doh or dol (type all that you got at 80, without '()' ) )___***")
        await message.channel.send("Example:")
        await message.channel.send("!updateMe Jane Grande 1 x pc ShadowBringers Tank Dps DoL healer DOH")


@fcSheet.client_discord.event
async def on_ready():
    print("started")


fcSheet.startConnectionToDiscord()

