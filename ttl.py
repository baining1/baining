# -*- coding: UTF-8 -*-
# 开发时间：2022/1/5 16:05

import time,sys,datetime
import requests, json
## 太太乐每天14点后会补货（可能变动）
#  CRON: * 14 * * *      （也可以 4-7 14 * * *  ,要兑换的时候改为  * 14 * * *）

## 如果出现请先登入，先打开小程序绑定微信
## 自动兑换需要先完善资料（打开太太乐餐厅app--个人中心--完善资料）

## 太太乐 格式 ：（"手机号","密码","联通"）,（"手机号","密码","移动"）（"手机号","密码","电信"）
## datam当前定时中第4,5,6,7分会执行签到和分享任务，其他时间只会监控库存自动兑换
datam=[4,5,6,7]
phonelist = [

]


###################################################################################
def printT(msg):
    print("[{}]: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), msg))
    sys.stdout.flush()

class Ttl(object):
    def get_headers(self, host='www.ttljf.com', token=''):
        headers = {
            "User-Agent": "otole/1.4.8 (iPhone; iOS 13.5; Scale/2.00)",
            "Host": host,
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
            "token": token,
            "Accept-Encoding": "gzip, deflate"
            # "Referer": referer
        }

        return headers

    def sign_in(self, username='', password=''):
        t = int(time.time())
        url = 'https://www.ttljf.com/ttl_site/user.do'
        post_data = 'username={}&password={}&device_brand=apple&device_model=iPhone11,8&device_uuid=&device_version=13.5&mthd=login&platform=ios&sign='.format(
            username, password)
        headers = self.get_headers()
        response = requests.post(url, data=post_data, timeout=(2, 2), headers=headers)
        data = json.loads(response.text)
        token = data['user']['loginToken']
        userId= data['user']['userId']
        return token,userId

    def my_integral(self, token):
        url = 'https://www.ttljf.com/ttl_chefHub/user/api/my'
        headers = self.get_headers(token=token)
        response = requests.get(url, timeout=(2, 2), headers=headers).json()
        return response["data"]["integral"]


    def stock(self,giftId):
        url = f'https://www.ttljf.com/ttl_site/giftApi.do?giftId={giftId}&mthd=giftDetail&sign=569aeaef6da7470ae38e4907aab980da&userId='
        response=requests.get(url,headers={"user_agent":"otole/1.4.8 (iPhone; iOS 13.5; Scale/2.00)"}).json()
        printT(f'{response["gifts"]["giftName"]},所需积分：{response["gifts"]["price"]},库存：{response["gifts"]["stockAmount"]}')
        stock_num =response["gifts"]["stockAmount"]
        return stock_num

    def stock2(self):
        id=["633","631","62","61"]
        stock_num=[]
        for giftId in id:
            url = f'https://www.ttljf.com/ttl_site/giftApi.do?giftId={giftId}&mthd=giftDetail&sign=569aeaef6da7470ae38e4907aab980da&userId='
            response=requests.get(url,headers={"user_agent":"otole/1.4.8 (iPhone; iOS 13.5; Scale/2.00)"}).json()
            printT(f'{response["gifts"]["giftName"]},所需积分：{response["gifts"]["price"]},库存：{response["gifts"]["stockAmount"]}')

    def exchange(self,token,userId,mobile,giftId):
        try:
            while True:
                url=f'https://www.ttljf.com/ttl_site/chargeApi.do?giftId={giftId}&loginToken={token}&method=charge&mobile={mobile}&sign=2bb51fe6302aa4ad5ebba9e123633fb3&userId={userId}'
                response = requests.get(url, headers={"user_agent": "otole/1.4.8 (iPhone; iOS 13.5; Scale/2.00)"}).json()
                printT(response["message"])
                if response["message"] !="成功":
                    break
        except :
            printT("兑换出错")

    ## 任务
    def ac_all(self, token):

        url1 = 'https://www.ttljf.com/ttl_chefHub/user/api/sign/today'
        headers = self.get_headers(token=token)
        response = requests.put(url1, timeout=(2, 2), headers=headers).json()
        printT(f'签到任务:{response["message"]}')

        url2 = 'https://www.ttljf.com/ttl_chefHub/Common/share/100858/activity'
        data = '{"id":100858,"type":"activity"}'
        response2 = requests.put(url2, timeout=(2, 2), headers=headers).json()
        printT(f'分享任务:{response2["message"]}')


if __name__ == '__main__':
    ttl = Ttl()
    ttl.stock2()

    printT("脚本:太太乐，当前共{0}个账号".format(len(phonelist)))
    for phone in phonelist:
        printT("".ljust(40, "#"))
        phponenum=phone[0]
        phponenum=phponenum[0:3]+'*****'+phponenum[8:]
        printT(f"开始执行账号:{phponenum},{phone[2]}")
        token,userId = ttl.sign_in(phone[0], phone[1])
        if int(datetime.datetime.now().strftime("%M")) in datam:   #30,31分执行
            ttl.ac_all(token)
        now_integral = ttl.my_integral(token)
        printT(f"现有积分:{now_integral}" )

        if phone[2]=="电信":
            if now_integral>=15:   #633 电信
                stockAmount = ttl.stock(633)
                if stockAmount !=0:
                    ttl.exchange(token,userId,phone[0],giftId=633)
                else:
                    printT("电信库存不足~~")
            else:
                printT("积分不足，再等等吧")

        elif phone[2]=="移动":
            if now_integral>=45:   #631 移动
                stockAmount = ttl.stock(631)
                if stockAmount!=0:
                    ttl.exchange(token,userId,phone[0],giftId=631)
                else:
                    printT("移动库存不足~~")
            else:
                printT("积分不足，再等等吧")

        elif phone[2]=="联通":
            if now_integral>=3:
                if now_integral>=7:     #62 联通5元
                    stockAmount = ttl.stock(62)
                    if stockAmount != 0:
                        ttl.exchange(token, userId, phone[0], giftId=62)
                    else:
                        printT("联通5元库存不足~~")
                stockAmount = ttl.stock(61)   #61 联通3元
                if stockAmount != 0:
                    ttl.exchange(token, userId, phone[0], giftId=61)
                else:
                    printT("联通2元库存不足~~")
            else:
                printT("积分不足，再等等吧")


