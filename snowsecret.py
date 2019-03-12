from cryptography.fernet import Fernet

def getValue():
  try:
    with open('/root/snowdata/key') as file:
      fern = Fernet(file.read())
    with open('/root/snowdata/user') as file:
      user = fern.decrypt(file.read()).decode("utf-8")
    with open('/root/snowdata/passwd') as file:
      passwd = fern.decrypt(file.read()).decode("utf-8")
    return (fern.decrypt(user).decode("utf-8"), fern.decrypt(passwd).decode("utf-8"))
  except:
    return ('','')
