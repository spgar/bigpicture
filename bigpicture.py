# bbigpicture crawls a subreddit and pulls out images/videos with large file sizes

import praw
from operator import itemgetter
from sys import stdout

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

subredditToProcess = 'funny'
submissionsToCheck = 50
topImageCount = 5

def getURLType(url):
    try:
        content = urlopen(url)
    except:
        return ''
    return content.info().maintype

def isImageOrVideoType(type):
    return ('image' in type) or ('video' in type)

def processURL(url):
    # If we have an image, then we can just use it
    if isImageOrVideoType(getURLType(url)):
        return url

    # If it's on imgur then we can just add .jpg and try again
    if 'imgur' in url and isImageOrVideoType(getURLType(url + '.jpg')):
        return url + '.jpg'

    # We can look at .mp4 size if on imgur with .gifv format
    if 'imgur' in url and 'gifv' in url:
        newURL = url.rsplit('.', 1)[0] + '.mp4'
        if isImageOrVideoType(getURLType(newURL)):
            return newURL

    # gfycat we'll rework and try again
    if 'gfycat' in url:
        newURL = 'https://giant.gfycat.com/' + url.rsplit('/', 1)[1] + '.gif'
        if isImageOrVideoType(getURLType(newURL)):
            return newURL

    # Can't resolve it, return empty
    return '';

def getFileSize(url):
    content = urlopen(url)
    try:
        fileSize = int(content.headers['content-length'])
    except:
        # Sometimes content-length is missing from the headers?
        # Sort them to the bottom of the list
        fileSize = -1
    return fileSize

print('Connecting to reddit (/r/{0})'.format(subredditToProcess))
r = praw.Reddit('SizeSearch 0.1')
subreddit = r.get_subreddit(subredditToProcess)

results = []
count = 0
print('Processing {0} latest submissions'.format(submissionsToCheck))
for submission in subreddit.get_new(limit=submissionsToCheck):
    url = submission.url
    try:
        processedURL = processURL(url)
        if processedURL:
            result = (url, getFileSize(processedURL))
            results.append(result)
    except:
        continue
    finally:
        count += 1

    stdout.write('\rProgress: (' + str(count) + '/' + str(submissionsToCheck) + ')')
    stdout.flush()

results = sorted(results, key=itemgetter(1), reverse=True)

print('')
print('Successfully processed {0} images.'.format(len(results)))
print('')
print('Top {0} largest images:'.format(min(topImageCount, len(results))))
for i in xrange(0, min(topImageCount, len(results))):
    print(results[i][0])