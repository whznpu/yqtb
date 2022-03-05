from distutils.log import error
import sys
from mysqlx import Session
import requests
import json 
import re

from sympy import content

# 准备url
yqtb_url="http://yqtb.nwpu.edu.cn"
uis_login_url = "https://uis.nwpu.edu.cn/cas/login?service=http%3A%2F%2Fyqtb.nwpu.edu.cn%2F%2Fsso%2Flogin.jsp%3FtargetUrl%3Dbase64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A%3D"
yqtb_detail_url= "http://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp"
yqtb_fillin_url = "http://yqtb.nwpu.edu.cn/wx/ry/" # 获取到签名和时间戳后拼接上去
# 指示是否成功
flag=True
# 指示是否成功发送填报数据并获取返回值
filled=False
# 服务器返回的状态信息
state="1"
# 服务器返回的错误信息
error=""

# 用户信息，通过参数读取
name=sys.argv[1]
studentId=sys.argv[2]
password=sys.argv[3]
webhook=""
try:
	webhook=sys.argv[4]
except:
	webhook=""



# print("姓名:"+name)
# print("学号:"+studentId)
# print("密码:"+"***")

# 请求疫情填报页面




try:
	session=requests.Session()
	response1 = session.get(yqtb_url)
	yqtb_cookie = session.cookies["JSESSIONID"] # 疫情填报的会话id
	uis_cookie=response1.cookies["SESSION"] #登录翱翔门户的id
	print("会话ID:"+yqtb_cookie)

	print(response1)
	#登录post的数据
	loginData = {
		"username" : studentId,
		"password" : password,
		"currentMenu" : 1,
		"execution" : "e1s1",
		"_eventId" : "submit",
		"geolocation" : "",
		"submit" : "稍等片刻……"
	}
	# 登录所用的cookie
	loginHeader={
		"Cookie":"SESSION="+uis_cookie
	}

	# 请求登录
	response2=session.post(uis_login_url,data=loginData,headers=loginHeader)
	print(response2)

	fillinData={
		"hsjc" : 1,
		"xasymt" : 1,
		"actionType" : "addRbxx",
		"userLoginId" : studentId,
		"szcsbm" : 1,
		"bdzt" : 1,
		"szcsmc" : "在学校",
		"sfyzz" : 0,
		"sfqz" : 0,
		"tbly" : "sso",
		"qtqksm" : "",
		"ycqksm" : "",
		"userType" : 2,
		"userName" : name
	}

	fillinHeader = {
		"Host" : "yqtb.nwpu.edu.cn",
		"Proxy-Connection" : "keep-alive",
		"Accept" : "application/json, text/javascript, */*; q=0.01",
		"X-Requested-With" : "XMLHttpRequest",
		"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
		"Content-Type" : "application/x-www-form-urlencoded",
		"Origin" : yqtb_url,
		"Referer" : yqtb_detail_url,
		"Accept-Encoding" : "gzip, deflate",
		"Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
		"Cookie" : "JSESSIONID=" + yqtb_cookie
	}
	# 获取提交所需要的签名和时间戳
	response3=session.get(yqtb_detail_url,headers=fillinHeader)
	print(response3)

	content=response3.content.decode('utf-8')
	print(type(content))
	f=open("test.txt","w+")
	f.write(str(content))
	f.close()
	extract=re.findall("ry_util.jsp.*(?=')",content)[0]
	print(extract)
	yqtb_fillin_url+=extract
	
	# 提交填报信息
	response4=session.post(url=yqtb_fillin_url,data=fillinData,headers=fillinHeader)
	print(response4)
	message=response4.text.strip().replace("\n","").replace("\r","").replace("——","-")
	print(message)
	dict=json.loads(message)
	filled=True
	state=dict["state"]
	print(state)
	if int(state)!=1:
		flag=False
		if "err-msg" in dict["err_msg"]:
			error=dict["err_msg"]
		else:
			error="未知错误信息"


except Exception as e:
	print(repr(e))
	# print("失败")
	flag=False


if flag:
	print("填报成功")
else:
	print("填报失败")
	if filled:
		print("错误码: "+str(state))
		print("错误信息: "+str(error))
