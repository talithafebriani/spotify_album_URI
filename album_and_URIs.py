#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import pandas as pd
import requests
import os
import time

# Constants
scope = 'user-top-read'
SPOTIPY_CLIENT_API1='241fd6ca81b9433697cebae67f729bb1'
SPOTIPY_CLIENT_API2='849421fda50e4bc8b99278ee1342ece5'
SPOTIPY_REDIRECT_URI='http://example.com/callback/'
cover_directory = "Covers/"
albums_per_artist = 10 #max 20

def main():

    tic = time.time()

    sys_args = sys.argv
    assert len(sys_args)==2, "A spotify username should be given as input \n Usage: python main.py <spotify_username>"
    spotify_username = sys_args[1]

    token = util.prompt_for_user_token( spotify_username ,scope,client_id=SPOTIPY_CLIENT_API1,client_secret=SPOTIPY_CLIENT_API2,redirect_uri=SPOTIPY_REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)
    top_artists = []

    for i in range(3): #getting different offset pages with each 20 artists
        artist_dict = sp.current_user_top_artists(limit = 20, offset = i, time_range='medium_term')
        top_artists = top_artists +artist_dict["items"]

    csv_rows = []
    f = open("Tagwriter_mass_encoding.csv", 'w')
    f.write("Type (Link/Text),Content (http://....),URI type (URI/URL/File...),Description,Interaction counter,UID mirror,Interaction counter mirror\n")

    for i,artist in enumerate(top_artists):
        artist_name = artist["name"]
        artist_name = ''.join(e for e in artist_name if e.isalnum() or e==" ")
        print(i,artist_name)
        mypath = cover_directory+str(i)+"-"+artist_name
        if not os.path.isdir(mypath):
            os.makedirs(mypath)

        albums = sp.artist_albums(artist["id"], limit = albums_per_artist)['items']
        album_names_list = []
        for album in albums:
            album_name = album["name"]
            album_uri = album["uri"]
            album_name_simple = ''.join(e for e in album_name if e.isalnum() or e==" ")
            if not album_name in album_names_list:
                album_url = album['images'][0]['url']
                img_data = requests.get(album_url).content
                with open(mypath+"/"+album_name_simple+".jpg", 'wb') as handler:
                    handler.write(img_data)
                csv_rows.append([artist_name, album_name_simple, album["uri"] ])
                description = artist_name+  ": " + album_name_simple
                description = description.encode('utf-8')
                f.write("Text,{0},,{1},,,\n".format(album["uri"], description  ) )
                print(csv_rows[-1])

    df = pd.DataFrame(csv_rows, columns = ['Artist', 'Album', 'Album_URI '])
    df.to_csv("artist_album_URI.csv", index = False, encoding = 'utf-8')
    f.close()
    toc = time.time() - tic
    print('---Finished the program in {0:.2f}s---'.format(toc))
    print('---Found {0:d} album covers for {1:d} artists---'.format(len(csv_rows), len(top_artists)))



if __name__ == '__main__':
    main()
