#coding=utf-8
from xml.etree import ElementTree as ET
from xml.dom import minidom
import numpy as np

def parse_xml():
    domobj = ET.parse(r"D:\OneDrive - pku.edu.cn\程序\DB_HW\user_ConcretInfo.xml")
    User = domobj.getroot()
    Username = User[0].text
    Info = User[1]
    BasicInfo = Info[0]
    OtherInfo = Info[1]
    Bs = []
    for child in BasicInfo:
        Bs.append(child.text)

    Posts = OtherInfo[0]
    Replies = OtherInfo[1]
    Ps = []
    for i,post in enumerate(Posts):
        Ps.append([])
        for child in post:
            Ps[i].append(child.text)
    Rs =[]
    for i,reply in enumerate(Replies):
        Rs.append([])
        for child in reply:
            Rs[i].append(child.text)
    return Bs,Ps,Rs


if __name__ == '__main__':
    bs,ps,rs = parse_xml()