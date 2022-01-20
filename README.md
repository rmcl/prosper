# Prosper Client

A python API client for the Prosper Lending Platform.


## Basic Example

```
from prosper.api import ProsperAPI

client = ProsperAPI.get_client_by_username_password(
    client_id='client id',
    client_secret=<client secret>',
    username='<username>',
    password='<password>')

notes_gen = client.notes()

print(len(list(notes_gen)))
> 80
```

## Structure of the library

This library has two files. api.py contains the API client which endeavors to mirror the API endpoints with the exception of transparently handling pagination. analysis.py contains pure python functions which perform some analysis or calculations I have found useful.


## Prosper API Docs

https://developers.prosper.com/docs/investor/
