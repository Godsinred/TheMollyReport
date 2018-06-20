import requests

KEY = "AIzaSyB_R-OTY2BwfqtjqWQ3eBPRfoTb8WywqFU"
url = r"https://maps.googleapis.com/maps/api/directions/json"
my_address = r"1334+Spectrum+Irvine+CA"
destination_address = r"1507+W+Nottingham+Lane+Anaheim+CA"
query = {"origin" : my_address, "destination" : destination_address, "key" : KEY}

r = requests.get(url, params=query)

print(r.url)
print(r)
print(r.content)
print(r.json())