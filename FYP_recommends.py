#!/usr/bin/env python
# coding: utf-8

# In[1]:


from django.shortcuts import render
from bson import json_util
import json
from django.http import JsonResponse
from difflib import SequenceMatcher
import pymongo
from bson import json_util, ObjectId
import random

myclient = pymongo.MongoClient("localhost", 27017)
mydb = myclient["Fyp"]
authorCol = mydb["Authors"]
pubCol = mydb["Publications"]


# In[8]:



getObj = {
    'author': [
        {
            'id': '5d7f18b8df762e7dd1f721a6', 
            'respect': 3
        }, 
        {
            'id': '5db3fc86ac323bff188aaa7e', 
            'respect': 1
        }
    ], 
    'publication': [
        {
            'id': '5d7f18bedf762e7dd1f721a7', 
            'respect': 2
        }
    ]
}

unsortedAuthorId = []
unsortedAuthorRespect = []
unsortedPublicationId = []
unsortedPublicationRespect = []

for i in getObj['author']:
    unsortedAuthorId.append(i['id'])
    unsortedAuthorRespect.append(i['respect'])

for i in getObj['publication']:
    unsortedPublicationId.append(i['id'])
    unsortedPublicationRespect.append(i['respect'])

# now selection sorting
# although no need to sort, it will only help in getting things first that is mostly viewed
authorId = []
authorRespect = []
publicationId = []
publicationRespect = []

for i in range(len(unsortedAuthorRespect)):
    maxx = max(unsortedAuthorRespect)
    authorRespect.append(maxx)
    authorId.append(unsortedAuthorId[unsortedAuthorRespect.index(maxx)])
    unsortedAuthorId.pop(unsortedAuthorRespect.index(maxx))
    unsortedAuthorRespect.pop(unsortedAuthorRespect.index(maxx))

for i in range(len(unsortedPublicationRespect)):
    maxx = max(unsortedPublicationRespect)
    publicationRespect.append(maxx)
    publicationId.append(unsortedPublicationId[unsortedPublicationRespect.index(maxx)])
    unsortedPublicationId.pop(unsortedPublicationRespect.index(maxx))
    unsortedPublicationRespect.pop(unsortedPublicationRespect.index(maxx))

noOfRecommendsbyAuthor = 6
noOfRecommendsbyPublications = 10
twentyfivePercentPublication = 2.0

totalPartsAuthor = 0
totalPartsPUblications = 0
for i in authorRespect:
    totalPartsAuthor += i
for i in publicationRespect:
    totalPartsPUblications += i

singleAuthorPartSize = noOfRecommendsbyAuthor/totalPartsAuthor
singlePublicationPartSize = noOfRecommendsbyPublications/totalPartsPUblications

authorPartsDivision = {}
publicationPartsDivision = {}

for idx, i in enumerate(authorId):
    singlePart = authorRespect[idx] * singleAuthorPartSize
    authorPartsDivision[i] = singlePart

for idx, i in enumerate(publicationId):
    singlePart = publicationRespect[idx] * singlePublicationPartSize
    publicationPartsDivision[i] = singlePart

spaceLeft = noOfRecommendsbyAuthor
uniqueRecommendations = []

returnObj = [
    {
        'id': '',
        'title': '',
        'year': '',
        'category': [],
        'author': '',
        'url': ''
    }
]

returnObj.pop() # either write it here or before return

# Author and Publication respects will take specific space from the limited recommendation size
# Author's publications will be recommended accordingly by random selection

for x, y in authorPartsDivision.items():
    reservedPlaces = round(y)
    if reservedPlaces > 0 and spaceLeft >= 0:
        # print('remaining no of spaces are: {}'.format(spaceLeft))
        tempObj = {
            'id': '',
            'title': '',
            'year': '',
            'category': [],
            'author': '',
            'url': ''
        }
        tempName = ''
        authorList = authorCol.find({'_id': ObjectId(x)})
        if authorList.count() > 0:
            tempName = authorList[0]['Name']
        publicationList = pubCol.find({'author':ObjectId(x)})
        publicationListIds = []
        publicationListIndexes = []
        if publicationList.count() > 0:
            allPublicationObjects = [
                {
                    'id': '',
                    'title': '',
                    'year': '',
                    'category': [

                    ],
                    'author': '',
                    'url': ''
                }
            ]
            allPublicationObjects.pop()
            for idx1, i in enumerate(publicationList):
                publicationListIndexes.append(idx1)
                tempPublication = {
                    'id': '',
                    'title': '',
                    'year': '',
                    'category': [

                    ],
                    'author': '',
                    'url': ''
                }
                tempPublication['id'] = i['_id']
                tempPublication['title'] = i['title']
                tempPublication['year'] = i['year']
                tempPublication['category'] = i['catogories']
                tempPublication['author'] = tempName
                tempPublication['url'] = i['papaerLink']
                uniqueRecommendations.append(i['title'])
                allPublicationObjects.append(tempPublication)
            if spaceLeft < 0:
                toBeRemoved = 0
                for i in range(0, spaceLeft, -1):
                    toBeRemoved += 1
                if len(publicationListIndexes) >= len(range(reservedPlaces - toBeRemoved)):
                    for i in random.sample(publicationListIndexes, len(range(reservedPlaces - toBeRemoved))):
                        returnObj.append(allPublicationObjects[i])
                else:
                    for i in random.sample(publicationListIndexes, len(publicationListIndexes)):
                        returnObj.append(allPublicationObjects[i])
            else:
                if len(publicationListIndexes) >= len(range(reservedPlaces)):
                    for i in random.sample(publicationListIndexes,len(range(reservedPlaces))):
    #                     print(publicationList[i])
    #                     print(publicationList.count())
    #                     print(publicationList)
    #                     for idx2, j in enumerate(publicationList):
    #                         if idx2 == i:
    #                             print('running if')
    #                             print(j)
    #                     print(allPublicationObjects[i])
                        returnObj.append(allPublicationObjects[i])

    #                     tempObj['id'] = str(publicationList[i]['_id'])
    #                     tempObj['title'] = publicationList[i]['title']
    #                     tempObj['year'] = publicationList[i]['year']
    #                     tempObj['category'] = publicationList[i]['category']
    #                     print(tempObj)
                else:
                    for i in random.sample(publicationListIndexes,len(publicationListIndexes)):
                        returnObj.append(allPublicationObjects[i])
        spaceLeft = spaceLeft - reservedPlaces

# Publication that takes 20% space will be returned 
spaceLeft = noOfRecommendsbyPublications

for x, y in publicationPartsDivision.items():
    reservedPlaces = round(y)
    if reservedPlaces > 0 and spaceLeft >= 0:
#         print('remaining no of spaces are: {}'.format(spaceLeft))
        tempObj = {
            'id': '',
            'title': '',
            'year': '',
            'category': [],
            'author': '',
            'url': ''
        }
        if y > twentyfivePercentPublication:
            # reserve one place from history
            thisPublication = pubCol.find_one({'_id': ObjectId(x)})

            tempObj['id'] = x
            tempObj['title'] = thisPublication['title']
            tempObj['year'] = thisPublication['year']
            tempObj['category'] = thisPublication['catogories']
            thisAuthor = authorCol.find_one({'_id': thisPublication['author']})
            tempObj['author'] = thisAuthor['Name']
            tempObj['url'] = thisPublication['papaerLink']
            if thisPublication['title'] not in uniqueRecommendations:
                returnObj.append(tempObj)
                publicationPartsDivision[x] = y - 1
                spaceLeft = spaceLeft - 1

allCategories = []
# all the categoires of publications are added

for x, y in publicationPartsDivision.items():
    thisPublication = pubCol.find_one({'_id': ObjectId(x)})
    allCategories += allCategories + thisPublication['catogories']

# see that max number of categories size in our db

maxSize = 0
for i in pubCol.aggregate([{'$group': {'_id': None, 'maxSize': {'$max': {'$size': '$catogories'}}}}]):
    maxSize = i['maxSize']

# combinational search in categories for greater than 2 because we surely can find single categories

# print('spaceLeft is : {}'.format(spaceLeft))

# requiredPublications = spaceLeft
searchMixedCategories = [2,3]
uniquePublications = []
timesLoopRuns = 0
timesLoopRuns2 = 0

while spaceLeft > 0:
    tempObj = {
        'id': '',
        'title': '',
        'year': '',
        'category': [],
        'author': '',
        'url': ''
    }
    oneOrTwo = random.sample(searchMixedCategories,1)[0]
    if len(allCategories) >= oneOrTwo:
        thisCategory = random.sample(allCategories, oneOrTwo)
    else:
        thisCategory = random.sample(allCategories, len(allCategories))
    thisPublication = pubCol.find({"catogories": {"$all": thisCategory}})
    selectedPublication = []
    if thisPublication.count() >= 1:
        selectedPublication = random.sample(list(thisPublication), 1)
        if selectedPublication[0]['title'] not in uniquePublications:
            timesLoopRuns = 0
            tempObj['id'] = str(selectedPublication[0]['_id'])
            tempObj['title'] = selectedPublication[0]['title']
            tempObj['year'] = selectedPublication[0]['year']
            tempObj['category'] = thisCategory
            thisAuthor = authorCol.find_one({'_id': selectedPublication[0]['author']})
            tempObj['author'] = thisAuthor['Name']
            tempObj['url'] = selectedPublication[0]['papaerLink']
            if selectedPublication[0]['title'] not in uniqueRecommendations:
                returnObj.append(tempObj)
                uniquePublications.append(selectedPublication[0]['title'])
                spaceLeft -= 1
            else: #this else will run if it only gets 1 publication again and again to stop the while loop
                timesLoopRuns2 += 1
                if timesLoopRuns2 == 5:
                    break
        else:
            timesLoopRuns += 1
            if timesLoopRuns == 10:
                break

for i in returnObj:
    print(i)
    print('\n\n')


# In[6]:


for i in range(0, -1, -1):
    print(i)


# In[ ]:




