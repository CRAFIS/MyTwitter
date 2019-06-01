# coding: utf-8

import MyTwitter
import time
import json
import sys
import datetime
import timeout_decorator

class LikeChecker():

    def __init__(self, user_name, list_name = None):
        self.twitter, self.user_id = MyTwitter.login(user_name)
        self.list_id = MyTwitter.getID(list_name) if list_name else ""
        self.friendList = MyTwitter.getListMember(self.twitter, self.list_id)
        self.friendList = [friend["id_str"] for friend in self.friendList] + [self.user_id]
        self.followList = MyTwitter.getFollowing(self.twitter, self.user_id)
        self.followList = [user for user in self.followList if user["id_str"] not in self.friendList]
        self.userList = []
        self.getDate = lambda date: str(MyTwitter.getDate(date))

    def checkFavorite(self, user, target):
        tweetList = MyTwitter.getFavTweetList(self.twitter, user["id_str"], 1000, target, loop = True)
        if tweetList == []: return None
        tweet = tweetList[-1]
        if tweet["user"]["id_str"] == target:
            date = self.getDate(tweet["created_at"])
            return date + "\n\n" + tweet["text"]
        date = "{0} ({1})".format(self.getDate(tweet["created_at"]), len(tweetList))
        return date + "\n\n" + "Not Found"

    def setup(self, count = 2000):
        self.userList = []
        tweetList = MyTwitter.getTweetList(self.twitter, self.user_id, count)
        for i, tweet in enumerate(tweetList):
            sys.stdout.write("\r{0}%".format(100*i//(len(tweetList)-1)))
            sys.stdout.flush()
            date = self.getDate(tweet["created_at"])
            text = date + "\n\n" + tweet["text"]
            favUserIDList = MyTwitter.getFavUserIDList(tweet["id_str"], self.friendList)
            userIDList = [user["id_str"] for user in self.userList]
            self.userList.extend([{"id_str": user_id, "text": text} for user_id in favUserIDList if user_id not in userIDList])
        followList = [friend["id_str"] for friend in self.followList]
        self.userList = [user for user in self.userList if user["id_str"] in followList]

    @timeout_decorator.timeout(10)
    def showLikeUser(self):
        nameList = MyTwitter.getUserList(self.twitter, [user["id_str"] for user in self.userList])
        for i, user in enumerate(self.userList):
            message = "{0}: {1}\n".format(i+1, nameList[i]["name"])
            message += "https://twitter.com/{0}\n\n".format(nameList[i]["screen_name"])
            message += user["text"]
            print("=" * 50 + "\n")
            print(message + "\n")

    def showNotLikeUser(self):
        print("↓ Not Like User ↓" + "\n")
        for friend in self.followList:
            if friend["id_str"] not in [user["id_str"] for user in self.userList] and friend["protected"] == False:
                print(friend["name"])
                print("https://twitter.com/" + friend["screen_name"] + "\n")

    def showProtectedUser(self):
        for i, friend in enumerate(self.followList):
            while friend["id_str"] not in [user["id_str"] for user in self.userList] and friend["protected"] == True:
                try:
                    response = self.checkFavorite(friend, self.user_id)
                    if response is not None:
                        message = friend["name"] + "\n"
                        message += "https://twitter.com/{0}\n\n".format(friend["screen_name"])
                        message += response
                        print(message + "\n")
                        print("=" * 50 + "\n")
                    break
                except:
                    time.sleep(60)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        LikeChecker = LikeChecker(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        LikeChecker = LikeChecker(sys.argv[1])
    else:
        print("Usage: python3 {0} [user_type] (exception_list_name)".format(sys.argv[0]))
        sys.exit()
    LikeChecker.setup()
    input("\n")
    while True:
        try:
            LikeChecker.showLikeUser()
            break
        except:
            pass
    input("=" * 50 + "\n")
    LikeChecker.showNotLikeUser()
    input("=" * 50 + "\n")
    LikeChecker.showProtectedUser()
