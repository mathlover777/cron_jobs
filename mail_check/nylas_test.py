import nylas


APP_ID = '5girg6tjmjuenujbsg0lnatlq'
APP_SECRET = '8fokx1yoht10ypwdgev3rqqlp'
token = 'mdAIdH097TNhRWF7GEMqaMi9tGH1Jy'
# client = nylas.APIClient(APP_ID, APP_SECRET, token)
# account = client.accounts


# print account

client = nylas.APIClient(APP_ID, APP_SECRET, token)
account = client.accounts

# Fetch the first thread
thread = account.threads.first()