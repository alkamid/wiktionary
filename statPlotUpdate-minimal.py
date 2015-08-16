import upload
import pywikibot

def update():

    targetFilename = 'Wzrost_Wikislownika.svg'
    fname = 'Wzrost_Wikislownika.svg'
    desc = 'update (2015/08)'

    bot = upload.UploadRobot([targetFilename], description=desc, keepFilename=True, verifyDescription=False, ignoreWarning=True, targetSite=pywikibot.getSite('commons', 'commons'))
    bot.run()


update()
