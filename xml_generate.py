#改一下主函数函数名
from xml.etree import ElementTree as ET
from xml.dom import minidom
def prettify(elem):
    rough_string = ET.tostring(elem,'utf-8')
    #print(type(rough_string))
    reparsed = minidom.parseString(rough_string)
    #print(type(reparsed))
    return reparsed.toprettyxml(indent = "\t",encoding="utf-8")
def generate_user_records(Username_p,BasicInfo_p,Posts_p,Replies_p):
    #root = ET.Element("person")
    #sub = ET.Element("pinfo",{"sex":"m","age":"21"},)
    #root.append(sub)
    #newstr = prettify(root)
    #file = open("news.xml","w",encoding = "utf-8")
    #file.write(newstr)
    #file.close()
    #以上test
    #root
    User = ET.Element("User")

    #subuser1
    Username = ET.Element("Username")
    Username.text = Username_p
    User.append(Username)
    #subuser2
    Info = ET.Element("Info")

    #subinfo1
    BasicInfo = ET.Element("BasicInfo")
    Gender = ET.Element("Gender")
    Gender.text = str(BasicInfo_p[0])
    Age = ET.Element("Age")
    Age.text = str(BasicInfo_p[1])
    Level = ET.Element("Level")
    Level.text = str(BasicInfo_p[2])
    Birthday = ET.Element("Birthday")
    Birthday.text = str(BasicInfo_p[3])
    BasicInfo.append(Gender)
    BasicInfo.append(Age)
    BasicInfo.append(Level)
    BasicInfo.append(Birthday)
    Info.append(BasicInfo)

    #subinfo2
    OtherInfo = ET.Element("OtherInfo")
    #subotherinfo1
    Posts = ET.Element("Posts")
    for ipost in Posts_p:
        Post = ET.Element("Post")
        No = ET.Element("No")
        No.text = str(ipost[0])
        Post.append(No)
        Block = ET.Element("Block")
        Block.text = str(ipost[1])
        Post.append(Block)
        PostUser = ET.Element("PostUser")
        PostUser.text = str(ipost[2])
        Post.append(PostUser)
        Title = ET.Element("Title")
        Title.text = str(ipost[4])
        Post.append(Title)
        Content = ET.Element("Content")
        Content.text = str(ipost[5])
        Post.append(Content)
        Clicks = ET.Element("Clicks")
        Clicks.text = str(ipost[7])
        Post.append(Clicks)
        ReplyNum = ET.Element("ReplyNum")
        ReplyNum.text = str(ipost[8])
        Post.append(ReplyNum)
        Posts.append(Post)
    #subotherinfo2
    Replies = ET.Element("Replies")
    for ireply in Replies_p:
        Reply = ET.Element("Reply")
        OriginalNo = ET.Element("OriginalNo")
        OriginalNo.text = str(ireply[0])
        Reply.append(OriginalNo)
        Floor = ET.Element("Floor")
        Floor.text = str(ireply[1])
        Reply.append(Floor)
        ReplyUser = ET.Element("ReplyUser")
        ReplyUser.text = str(ireply[2])
        Reply.append(ReplyUser)
        ReplyContent = ET.Element("ReplyContent")
        ReplyContent.text = str(ireply[5])
        Reply.append(ReplyContent)
        ReplyTime = ET.Element("ReplyTime")
        ReplyTime.text = str(ireply[6])
        Reply.append(ReplyTime)
        PraiseNum = ET.Element("PraiseNum")
        PraiseNum.text = str(ireply[7])
        Reply.append(PraiseNum)
        Replies.append(Reply)
    OtherInfo.append(Posts)
    OtherInfo.append(Replies)
    Info.append(OtherInfo)
    User.append(Info)

    newstr = prettify(User)
    #在apache启动下，文件在apache根目录中
    file = open("user_ConcretInfo.xml","wb+")
    file.write(newstr)
    file.close()


if __name__ =="__main__":
    a = 1