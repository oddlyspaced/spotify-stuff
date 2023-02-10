# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 08:33:28 2021

This script contains functions used in the Generalized Spotify Analyser

@author: olehe

"""


# some general imports

import pandas as pd
import time
import os.path
import random
import spotipy.oauth2 as oauth2
import spotipy


# Import credentials
import spotifyConstants

sp_oauth = oauth2.SpotifyOAuth(client_id=spotifyConstants.myClientID,
								   client_secret=spotifyConstants.myClientSecret,
								   redirect_uri=spotifyConstants.myRedirect,
								   username=spotifyConstants.myUser,
								   scope=None)

# create global sp? Not sure what is best, re parallelizing
# if global, then would need to update auth


sp = []

#%% Authenticate

def authenticate():
	#global token_info, sp_oauth, token
	global sp, sp_oauth
	sp = spotipy.Spotify(auth_manager=sp_oauth)
	
	# do a search to initiate
	not_output = sp.me()
	
	'''
	token_info = sp_oauth.get_cached_token()
	if not token_info:
		auth_url = sp_oauth.get_authorize_url()
		print('\n')
		print(auth_url)
		print('\n')
		# try to put the link in the clipboard
		pd.DataFrame([auth_url]).to_clipboard(index=False, header=False)
		
		
		# If the session hangs at this line, just paste the reponse manually into response.
		response = input('Paste the above link into your browser (it is in your clipboard), then paste the redirect url here: ')
		code = sp_oauth.parse_response_code(response)
		
		
		# Note a deprecation warning with this one. 
		token_info = sp_oauth.get_access_token(code)
		
	if sp_oauth.is_token_expired(token_info):
			token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
			token = token_info['access_token']
			print('Refreshed token')
	'''		
	#token = token_info['access_token']
	#global sp
	#sp = spotipy.Spotify(auth=token)
	return

#%% this function checks of the token is expired, and refreshes it if so 
# Call this before every call to sp.
def refresh():
	
	output = 0
	print('Refresh temporarily unstable. Working on fix.')
	'''
	token_info = sp_oauth.get_cached_token()
	if sp_oauth.is_token_expired(token_info):
			token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
			#token = token_info['access_token']
			print('Refreshed token')
			output = 1
	'''
	return output


#%% Function for getting information
def getInformation(thisList, verbose=False):
	# make a filename to save it to
	# also, return this filename
	global sp
	
	thisSaveName = 'Playlists/' + thisList + '.pkl'
	
	# now check if the file already exists
	if os.path.isfile(thisSaveName):
		return thisSaveName
	
	
	
	#refresh()

	if verbose:
		print('Getting audio features and information from playlist.')
	
	if not os.path.exists('Playlists'):
		os.makedirs('Playlists')

	'''
	#refresh()
	authenticate()
	token_info_cached = sp_oauth.get_cached_token()
	token_info = sp_oauth.refresh_access_token(token_info_cached['refresh_token'])
	token = token_info['access_token']
	sp = spotipy.Spotify(auth=token)
	'''
	

	column_names = ['playlistID','TrackName', 'TrackID', 'SampleURL', 'ReleaseYear', 'Genres', 'danceability', 'energy', 
				'loudness', 'speechiness', 'acousticness', 'instrumentalness',
				'liveness', 'valence', 'tempo', 'key', 'mode', 'duration_ms']
	sampleDataFrame = pd.DataFrame(columns = column_names)
	# Sleep a little bit to not piss of Spotify
	thisSleep = random.randint(0,10) * 0.01
	time.sleep(thisSleep)
	
	
	
	# refresh token
	#refresh()
	try:
		theseTracks = sp.playlist_tracks(thisList, limit=None)
	except:
		# handle errors with getting tracks
		theseTracks = 0
		thisDict = [{'playlistID':'EMPTYDATAFRAME',
				 'TrackName':'EMPTYDATAFRAME',
				 'TrackID':'EMPTYDATAFRAME',
				 'SampleURL':'EMPTYDATAFRAME',
				 'ReleaseYear': 'EMPTYDATAFRAME',
				 'Genres':'EMPTYDATAFRAME',
				 'Popularity':-1,
				 'danceability':0,
				 'energy':0,
				 'loudness':0,
				 'speechiness':0,
				 'acousticness':0,
				 'instrumentalness':0,
				 'liveness':0,
				 'valence':0,
				 'tempo':0,
				 'key':0,
				 'mode':0,
				 'duration_ms':0
				 }]
		thisDf = pd.DataFrame(thisDict)
		sampleDataFrame = sampleDataFrame.append(thisDf, ignore_index=True)
		return 'error'
		

	# Make sure to get all tracks in a playlist
	tracks = theseTracks['items']
	while theseTracks['next']:
		#authenticate()
		theseTracks = sp.next(theseTracks)
		tracks.extend(theseTracks['items'])
	
	for track in tracks:
		if track['track']==None:
			continue
		thisId=track['track']['id']
		if thisId == None:
			continue
		thisName=track['track']['name']
		if verbose:
			print('Current track: ' + thisName)

		
		thisReleaseDate = track['track']['album']['release_date']
		thisPopularity = track['track']['popularity']
		
		if thisPopularity == None:
			thisPopularity=-1
		
		if thisReleaseDate == None:
			thisReleaseDate = 0
			
		# genre is linked to artist, not to song. Therefore, need another get here.
		# first get artist.
		# will get the first artist, there might be numerous

		thisArtistId = track['track']['artists'][0]['id']
		if thisArtistId == None:
			thisGenres = '[unknown]'
		else:
			#refresh()
			try:
				thisArtistInfo = sp.artist(thisArtistId)
				thisGenres = thisArtistInfo['genres']
			except:
				thisGenres = []
			if thisGenres == []:
				thisGenres = '[unknown]'
		
		
		thisUrl=track['track']['preview_url']
		# Sleep a little bit to avoid rate limiting
		thisSleep = random.randint(0,10)*0.09
		time.sleep(thisSleep)
		# Get audio features for the track
		'''
		update = refresh()
		if update == 1:
			token_info = sp_oauth.get_cached_token()
			token = token_info['access_token']
			sp = spotipy.Spotify(auth=token)
		authenticate()
		'''
		thisFeature=sp.audio_features(tracks=thisId)
		
		# Create a dataframe entry
		if thisFeature[0]!=None:
			thisDict = [{'playlistID':thisList,
				 'TrackName':thisName,
				 'TrackID':thisId,
				 'SampleURL':thisUrl,
				 'ReleaseYear': thisReleaseDate,
				 'Genres':thisGenres,
				 'Popularity':thisPopularity,
				 'danceability':thisFeature[0]['danceability'],
				 'energy':thisFeature[0]['energy'],
				 'loudness':thisFeature[0]['loudness'],
				 'speechiness':thisFeature[0]['speechiness'],
				 'acousticness':thisFeature[0]['acousticness'],
				 'instrumentalness':thisFeature[0]['instrumentalness'],
				 'liveness':thisFeature[0]['liveness'],
				 'valence':thisFeature[0]['valence'],
				 'tempo':thisFeature[0]['tempo'],
				 'key':thisFeature[0]['key'],
				 'mode':thisFeature[0]['mode'],
				 'duration_ms':thisFeature[0]['duration_ms']
				 }]
			thisDf = pd.DataFrame(thisDict)
			sampleDataFrame = pd.concat([sampleDataFrame, thisDf], ignore_index=True)

	
	# do a check here to see if empty 
	if sampleDataFrame.empty:
		thisDict = [{'playlistID':'EMPTYDATAFRAME',
				 'TrackName':'EMPTYDATAFRAME',
				 'TrackID':'EMPTYDATAFRAME',
				 'SampleURL':'EMPTYDATAFRAME',
				 'ReleaseYear': 'EMPTYDATAFRAME',
				 'Genres':'EMPTYDATAFRAME',
				 'Popularity':-1,
				 'danceability':0,
				 'energy':0,
				 'loudness':0,
				 'speechiness':0,
				 'acousticness':0,
				 'instrumentalness':0,
				 'liveness':0,
				 'valence':0,
				 'tempo':0,
				 'key':0,
				 'mode':0,
				 'duration_ms':0
				 }]
		thisDf = pd.DataFrame(thisDict)
		sampleDataFrame = sampleDataFrame.append(thisDf, ignore_index=True)
		
	# save as pickle here
	sampleDataFrame.to_pickle(thisSaveName)
	return thisSaveName