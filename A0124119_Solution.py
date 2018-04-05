import json
import copy


def read_json(file):
    datafile = open(file, 'r', encoding='utf-8')
    return json.loads(datafile.read())


fb_data = read_json("cs1010s-fbdata.json")


def count_comments(data):
    num_com = 0
    messages = data["feed"]["data"]
    for i in messages:
        if "comments" in i.keys():
            num_com += len(i["comments"]["data"])

    return num_com


def count_likes(data):
    num_like = 0
    messages = data["feed"]["data"]
    for i in messages:
        if "likes" in i.keys():
            num_like += len(i["likes"]["data"])
        if "comments" in i.keys():
            comments = i["comments"]["data"]
            for j in comments:
                if "like_count" in j.keys():
                    num_like += j["like_count"]

    return num_like


def create_member_dict(data):
    member_dict = {}
    for i in data["members"]["data"]:
        if "gender" in i.keys():
            member_dict[i["id"]] = {"name": i["name"], "gender": i['gender']}
        else:
            member_dict[i["id"]] = {"name": i["name"]}

    return member_dict


# Why did we choose the id of the member data object to be the key?
# member id is unique for each member, hence there will be no conflict when creating a new key
# It is inappropriate to use the name as the key. What will happen if we use name as
# the key of member_dict?
# Two or members may have the same name, hence when you add the details of the second or subsequent member using
# the name key, one key may end up holding the details of multiple members, hence making data retrieval a pain.

def posts_freq(data):
    posts = {}
    messages = data["feed"]["data"]
    for i in messages:
        iden = i["from"]["id"]
        if iden in posts.keys():
            posts[iden] += 1
        else:
            posts[iden] = 1

    return posts


def comments_freq(data):
    comments = {}
    messages = data["feed"]["data"]
    for i in messages:
        if "comments" in i:
            fbcomments = i["comments"]["data"]
            for j in fbcomments:
                iden = j["from"]["id"]
                if iden in comments.keys():
                    comments[iden] += 1
                else:
                    comments[iden] = 1

    return comments


def likes_freq(data):
    final = {}
    messages = data["feed"]["data"]
    for i in messages:
        if "likes" in i.keys():
            likes = i["likes"]["data"]
            for j in likes:
                if j["id"] in final.keys():
                    final[j["id"]] += 1
                else:
                    final[j["id"]] = 1

    return final


def popularity_score(data):
    final = {}
    comment_final = {}
    messages = data["feed"]["data"]
    for i in messages:
        if "likes" in i.keys():
            iden = i["from"]["id"]
            if iden in final.keys():
                final[iden] += len(i["likes"]["data"])
            else:
                final[iden] = len(i["likes"]["data"])

        if "comments" in i.keys():
            comments = i["comments"]["data"]
            for j in comments:
                if j["from"]["id"] in comment_final.keys():
                    comment_final[j["from"]["id"]] += j["like_count"]
                else:
                    comment_final[j["from"]["id"]] = j["like_count"]

    for key in comment_final:
        if key in final.keys():
            final[key] += comment_final[key]
        else:
            final[key] = comment_final[key]

    copy_final = copy.deepcopy(final)
    for key in copy_final:
        if final[key] == 0:
            del final[key]

    return final


def member_stats(data):
    stats = create_member_dict(data)
    posts_count = posts_freq(data)
    comments_count = comments_freq(data)
    likes_count = likes_freq(data)
    for key in stats:
        if key in posts_count.keys():
            stats[key]["posts_count"] = posts_count[key]
        else:
            stats[key]["posts_count"] = 0
        if key in comments_count.keys():
            stats[key]["comments_count"] = comments_count[key]
        else:
            stats[key]["comments_count"] = 0
        if key in likes_count.keys():
            stats[key]["likes_count"] = likes_count[key]
        else:
            stats[key]["likes_count"] = 0

    return stats


def activity_score(data):
    stats = member_stats(data)
    score = {}

    for key in stats:
        score[key] = stats[key]["posts_count"] * 3 + stats[key]["comments_count"] * 2 + stats[key]["likes_count"]

    return score


def active_members_of_type(data, k, freq):
    info = create_member_dict(data)
    frequency = freq(data)
    final_list = []
    for key in frequency:
        if key in info.keys():
            final_list.append([info[key]["name"], frequency[key]])

    final_list.sort(key = lambda x: x[1])
    for i in final_list.copy():
        if i[1] < k:
            final_list.remove(i)
        else:
            break
    final_list.sort(key=lambda x: [-x[1], x[0]], reverse=False)
    return final_list