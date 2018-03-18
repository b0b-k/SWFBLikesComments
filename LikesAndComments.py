
#import networkx as nx 
#from networkx.readwrite import json_graph
#import operator
import requests
import facebook 
import json
import sys

token='FB-Token'
g = facebook.GraphAPI(access_token = token)

name = sys.argv[1]
getData = 'https://graph.facebook.com/v2.12/%s/posts?fields=likes.limit(1).summary(true),reactions.limit(1).summary(true),comments.limit(300).summary(true),message&access_token=%s'%(name,token)
data = requests.get(getData)

f = open('%s.txt'%name.replace('.',' '),'w')

posts = json.loads(data.content)['data']
f.write('number of posts is %d\n\n'%len(posts))

totalLikes = 0
totalComments = 0
totalLikesPercentage = 0.0
totalCommentsPercentage = 0.0
totalEmptyCommentsPercentage = 0.0
maxLikesPercentage = 0
maxCommentsPercentage = 0
#set maxLikedPost and MaxCommentedPost to first post
maxLikedPost = posts[0]['message'] if 'message' in posts[0] else ''
maxCommentedPost = maxLikedPost
for post in posts:
    message = ''
    if 'message' in post:
        message = post['message']
    likes = post['likes']['summary']['total_count']
    comments = post['comments']['data']
    commentsTotalCount = post['comments']['summary']['total_count']
    #get comments paging to loop over all the comments
    commentsPaging = ''
    if 'paging' in post['comments']:   
            commentsPaging = post['comments']['paging']
    #empty comments = GIF,Photo or Video Comments
    emptyCommentsCount = 0
    commentCount = 0
    for comment in comments:
        commentCount += 1
        if comment['message'] == '':
            emptyCommentsCount += 1
    
    while 'next' in commentsPaging:
        
        next = commentsPaging['next']
        data = requests.get(next)
        moreComments = json.loads(data.content)['data']
        for comment in moreComments:
            commentCount += 1
            if comment['message'] == '':
                emptyCommentsCount += 1
        #keep looping through comments        
        if 'paging' in json.loads(data.content):   
            commentsPaging = json.loads(data.content)['paging']
        else:
            commentsPaging = ''
            
    
    otherReactions = post['reactions']['summary']['total_count'] - likes
    likesPercentage = (likes+otherReactions)*100.0/(likes+otherReactions+commentCount) if (likes+otherReactions+commentCount) != 0 else 0
    commentsPercentage = commentCount*100.0/(likes+otherReactions+commentCount) if (likes+otherReactions+commentCount) != 0 else 0
    emptyCommentsPercentage = emptyCommentsCount*100.0/commentCount if commentCount != 0 else 0
    
    totalLikes += (likes+otherReactions)
    totalComments += commentCount
    
    totalLikesPercentage += likesPercentage
    totalCommentsPercentage += commentsPercentage
    totalEmptyCommentsPercentage += emptyCommentsPercentage
    
    newMaxLikes = max(maxLikesPercentage, likesPercentage)
    if maxLikesPercentage != newMaxLikes:
        maxLikedPost = message
    maxLikesPercentage = newMaxLikes  
    
    newMaxComments = max(maxCommentsPercentage, commentsPercentage)
    if maxCommentsPercentage != newMaxComments:
        maxCommentedPost = message
    maxCommentsPercentage = newMaxComments   
    
    f.write('--------------------------\n<post: %s> - <likes: %d>  - <other reactions: %d> - <comments: %d> - <gifComments: %d> - <percentages likes,comments,emptycomments>: %.2f %.2f %.2f \n--------------------------\n'%(message.encode('utf-8'),likes,otherReactions,commentCount,emptyCommentsCount,likesPercentage,commentsPercentage,emptyCommentsPercentage))
f.write('\n\n Averages: Likes: %d - Comments: %d ------- percentages Average: Likes: %.2f   - Comments: %.2f   - EmptyComments:  %.2f\n\n'%(totalLikes/len(posts),totalComments/len(posts),totalLikesPercentage/len(posts),totalCommentsPercentage/len(posts),totalEmptyCommentsPercentage/len(posts)))
f.write('--------------------------\n<max liked post: %s> \n--------------------------\n'%(maxLikedPost.encode('utf-8')))
f.write('--------------------------\n<max Commented post: %s> \n--------------------------\n'%(maxCommentedPost.encode('utf-8')))
f.close()    
