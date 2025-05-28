import json

thisConvo = """
{Rahul} I heard someone say my popularity plummeted what does that even mean

{Modi} It means to fall rapidly Rahul like how your party does after every election result

{Rahul} Arrey so rude I was just asking

{Shashi} Plummet is a verb it means to drop suddenly and steeply for example stock prices can plummet or public opinion can plummet especially after questionable speeches

{Rahul} So basically it is a fancy word for falling fast

{Modi} Yes very fast like petrol prices in dreams only

{Shashi} Or like attention spans when someone speaks without a point which sadly plummets hope
"""



def getPersonVoice(personName: str):
    with open("profiles/userProfiles.json", "r") as f:
        data = json.load(f)
        # The users field is an object, not a list, so we iterate over its values
        for user_key, user_data in data["users"].items():
            if user_data["displayName"].lower() == personName.lower():
                return user_data["audioFile"]
    return None

eachLine = thisConvo.split("\n")

for line in eachLine:
    if line == "":
        continue
    personName = line.split("}")[0].split("{")[1]
    lineData = line.split("}")[1].strip()
    voiceFile = getPersonVoice(personName)
    print(personName,':', lineData)
    print(voiceFile)



