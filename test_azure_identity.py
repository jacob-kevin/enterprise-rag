from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

token = credential.get_token('https://database.windows.net/.default')

print("SUCCESSSS")
print(token.token[:50])