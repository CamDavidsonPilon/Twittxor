import random
import re

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext



import twitter

def home(request):
    request.session['score']=0
    request.session['attempts']=0
    return render_to_response('home.html', context_instance = RequestContext(request))

def display( request ):
    CONSUMER_KEY = "2JKm08FiwMOzkz4NkZG6g"
    CONSUMER_SECRET = "PD7Vsf1PFaILm9299ZJ9229OurUWu2u4FxBF5IyeUI0"

    ACCESS_TOKEN_KEY = "485377093-RFE1Kis68GiDQS6OEXzc8aZ5Toa5g4pnfQqh1P46"
    ACCESS_TOKEN_SECRET = "VDgbgoeqfJ4T5E81mGTL4M60RXHIHG4r8lVp5bkU8"
    
    api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    
    #have js in the front end to check for non-empty input!!
    try:
        username = request.GET['screen_name']
    except:
        statuses = api.GetPublicTimeline()
        i=0
        while (1):
            if "\\x" not in statuses[i].text: #check for unicode. We only want english speakers.
                username = str(statuses[i].user.screen_name) #find a random user.
                break
         #what happens if they are all unicode?
        if i>25:
            username = str(statuses[0].user.screen_name)
    try:
        request.session['score']+=int(request.GET['right'])
        request.session['attempts']+=1
    except:
        pass
    
    #find two followers of the user.
    try:
        ids = api.GetFriendIDs(user=username)['ids']
    except twitter.TwitterError:
        #this user does not exist.
        return render_to_response('home.html', {'error':"The user name does not exist."}, context_instance = RequestContext(request)  )
    #ok ids has returned a list. Make sure there are more than 1 following
    lenID = len(ids)
    if lenID<2:
        return render_to_response('home.html',{ 'error': "This user does not have enough followers."}, context_instance = RequestContext(request) )
    #get two of the ids, randomly. 
    random.shuffle(ids)

    i = 0
    while (1):
        userID1 = ids[i]
        userID2 = ids[i+1]
        try:
            #the user might not be authorized, whatever that means...
            tweets = api.GetUserTimeline(user_id = userID1)
            other = api.GetUserTimeline(user_id = userID2)
            if len(tweets)>0 and len(other)>0:
                break
            else:
                i+=1
        except:
            pass
        i+=1
            
    #get the screen names, description and profile images.
    screen_name2 = other[0].user.screen_name 
    description2 = other[0].user.description
    profile_image_url2 = other[0].user.profile_image_url
    
    screen_name1 = tweets[0].user.screen_name
    description1 = tweets[0].user.description
    profile_image_url1 = tweets[0].user.profile_image_url
        
    #I'm also going to check if the msg contains '@', and not choose it if it does.
    i=0
    if random.random<0.5:
        sol = 1
        while(1):
            text = tweets[random.randint(0,len(tweets)-1)].text
            i +=1
            if (('@' not in text) and ('\\x' not in text) ) :
                break
            if i>100:
                #throw some error, as it is likely the user does not have any non-@ tweets.
                break
    else:
        sol = 2
        while(1):
            text = other[random.randint(0,len(other)-1)].text
            i+=1
            if '@' not in text:
                break 
            if i>100:
                break
                
                
    #turn any links into hyperlinks
    m = re.search("(.[^\s])*\.[a-z][a-z]\/([^\s])*", text)
    if m:
       l,u = m.span()
       text = text[0:l] + '<a href="%s">'%m.group() + m.group() + '</a>'+ text[u:]
    
    dict_to_send = {'text': text,
                    'screen_name1': screen_name1,
                    'screen_name2': screen_name2,
                    'description1': description1,
                    'description2': description2,
                    'profile_image_url2':profile_image_url2,
                    'profile_image_url1':profile_image_url1,
                    'username':username,
                    'sol': sol,
                    'session':request.session,
                    }
    return render_to_response('home.html', dict_to_send, context_instance = RequestContext(request) ) 
    
