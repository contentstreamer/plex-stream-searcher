import requests
import json
import time
import webbrowser
import config

def plex_call(url):
	plexToken = {"X-Plex-Token":config.PLEX_TOKEN}
	headers = {'Accept': 'application/json'}
	librariesresponse = requests.get(url, headers=headers, params=plexToken)
	return librariesresponse.json()

allplexlibraries = plex_call(config.PLEX_URL + "/library/sections")

print("Your Plex Libraries")
libs = allplexlibraries['MediaContainer']['Directory']
libArray = {}

for lib in libs:
	libKey = lib['key']
	libType = lib['type']
	libArray[libKey] = libType
	print(lib['key'],lib['title'])
chooseLibrary = input("Choose Library: ")

chosenLibrary = plex_call(config.PLEX_URL + "/library/sections/" + chooseLibrary + "/all")

libItems = chosenLibrary['MediaContainer']['Metadata']
libType = chosenLibrary['MediaContainer']['viewGroup']
libTitle = chosenLibrary['MediaContainer']['librarySectionTitle']

message = """<html>
<head>
	<title>Plex Searcher - """ + libTitle + """</title>
	<link rel="stylesheet" href="style.css">
</head>
<body>
	<h3>Plex Searcher - """ + libTitle + """</h3>
<table>
	<thead>
		<tr>
			<th>Plex</th>
			<th>Available</th>
		</tr>
	</thead>"""


for item in libItems:
	if 'title' in item and 'year' in item:
		plexItemTitle = item['title']
		plexItemYear = item['year']
		print('Plex searching ' + libTitle + ': ' + plexItemTitle, plexItemYear)        		

		message += """<tr><td>""" + plexItemTitle + """ (""" + str(plexItemYear) + """)</td>"""

		searchurl = "https://apis.justwatch.com/content/titles/en_GB/popular"
		searchquerystring = {"language":"en"}
		searchpayload = '{"page_size": 1,"page": 1,"query": "' + plexItemTitle + '","content_types": ["'+libType+'"]}'

		searchresponse = requests.post(searchurl, data=searchpayload, headers={}, params=searchquerystring)
		searchjson = searchresponse.json()
		
		streams = searchjson['items']
		
		for stream in streams:
			streamtitle = stream['title']
			if 'original_release_year' in stream:
				streamyear = stream['original_release_year']
				if abs(streamyear-plexItemYear) <= 1:
					offersAvailable = True if "offers" in stream else False
					if(offersAvailable == True):
						if 'offers' in stream:
							message += """<td>"""
							offers = stream['offers']
							for offer in offers:
								monetization_type = offer['monetization_type']
								presentation_type = offer['presentation_type']
								provider_id = offer['provider_id']
								if(monetization_type in ['flatrate','free']):
									if 'urls' in offer:
										viewUrl = offer['urls']['standard_web']
										print('-- can be deleted: ' + plexItemTitle, plexItemYear, presentation_type, viewUrl)
										message +=  """<a target='_blank' href='""" + viewUrl + """'>""" + viewUrl + """ ("""+presentation_type +""")</a>""" + """<BR>"""
		message += """ </td></tr> """
message += """</p></body></html>"""

timestr = time.strftime("%Y%m%d-%H%M%S")
pageName = libTitle.replace(" ", "-") + '-' +  timestr + '.html'
f = open(pageName,'w')
f.write(message)
f.close()

filename = config.RUN_PATH + pageName
webbrowser.open_new_tab(filename)