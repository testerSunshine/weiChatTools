import re
import time
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt  # 解除csrf验证
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic

# 微信服务器推送消息是xml的，根据利用ElementTree来解析出的不同xml内容返回不同的回复信息，就实现了基本的自动回复功能了，也可以按照需求用其他的XML解析方法
import xml.etree.ElementTree as ET

import top

conf = WechatConf(  # 实例化配置信息对象
    token='weixin',  # 服务器配置-Token
    appid='wxa0a9f38b9d029cb8',  # 公众号开发信息-开发者ID
    appsecret='cef2906434dddcb16dd24d6d121dd776',  # 公众号开发信息-开发者密码
    encrypt_mode='normal',  # 服务器配置-明文模式
    encoding_aes_key='JoxHmnGE9p2gNR40faQObxqXeZtA3FoUItg4i7hCMoo'  # 服务器配置-EncodingAESKey
)


@csrf_exempt  # 去除csrf验证
def wechat(request):
    if request.method == "GET":
        signature = request.GET.get('signature')  # 获取请求信息
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        wechat_instance = WechatBasic(conf=conf)  # 实例化微信基类对象
        if not wechat_instance.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):  # 检查验证请求的签名
            return HttpResponseBadRequest('Verify Failed')
        else:
            if request.method == 'GET':
                return HttpResponse(request.GET.get('echostr', None))  # 返回请求中的回复信息
    else:
        othercontent = autoreply(request)
        return HttpResponse(othercontent)


def autoreply(request):
    try:
        webData = request.body
        xmlData = ET.fromstring(webData)

        msg_type = xmlData.find('MsgType').text
        ToUserName = xmlData.find('ToUserName').text
        Content = xmlData.find('Content').text
        FromUserName = xmlData.find('FromUserName').text
        CreateTime = xmlData.find('CreateTime').text
        MsgType = xmlData.find('MsgType').text
        MsgId = xmlData.find('MsgId').text

        toUser = FromUserName
        fromUser = ToUserName

        if msg_type == 'text':
            t = TBKParams()
            print("收到消息", Content)
            if "￥" in Content:  # 判断是否有口令
                content = t.getCouponByName(Content)
            elif "你叫" in Content:
                content = "我叫十八，你呢"
            else:
                content = "暂时还不知道你说的是什么，试试回复 '你叫' "
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()

        elif msg_type == 'image':
            content = "图片已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        elif msg_type == 'voice':
            content = "语音已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        elif msg_type == 'video':
            content = "视频已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        elif msg_type == 'shortvideo':
            content = "小视频已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        elif msg_type == 'location':
            content = "位置已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        else:
            msg_type == 'link'
            content = "链接已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()

    except Exception as Argment:
        return Argment


class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class TBKParams:
    ERROR_INFO = "未查询到优惠券,您可以换一个商品十八再为您查询，或者回复 '当日' 就可以获得很多优惠券奥"

    def __init__(self):
        """
        """
        self.appkey = 25427003
        self.secret = "edc28fb0f5ff043dd032ae02c29992a2"
        self.adzone_id = 74469850460

    def get_tb_coupons(self, keyword):
        req = top.api.TbkDgItemCouponGetRequest()
        req.set_app_info(top.appinfo(self.appkey, self.secret))
        #
        req.adzone_id = self.adzone_id
        req.platform = 1
        req.cat = "16,18"
        req.page_size = 20
        req.q = keyword
        req.page_no = 1
        try:
            resp = req.getResponse()
            print(resp)
        except Exception as e:
            print("错误", e)

    def convertRequestGoods(self, password_content):
        req = top.api.WirelessShareTpwdQueryRequest()
        req.set_app_info(top.appinfo(self.appkey, self.secret))
        req.password_content = password_content
        try:
            resp = req.getResponse()
            print(resp)
        except Exception as e:
            print("错误", e)

    def getCouponByName(self, TKL):
        """
        根据商品名称查询是否有优惠券
        :param name:
        :return:
        """
        name_re = re.compile("【(.*)】")
        name = re.search(name_re, TKL).group(1)
        print("本次查询的商品名字为:", name)
        req = top.api.TbkDgMaterialOptionalRequest()
        req.set_app_info(top.appinfo(self.appkey, self.secret))
        req.adzone_id = self.adzone_id
        req.q = name
        req.has_coupon = "true"
        try:
            resp = req.getResponse()
            if resp and "tbk_dg_material_optional_response" in resp:
                couponResult = resp["tbk_dg_material_optional_response"]["result_list"]["map_data"]
                couponData = "感谢您的耐心等待，为您找到下面优惠券:\n"
                couponInfo = ""
                for index in range(len(couponResult)):
                    title = couponResult[index].get("title", "")  # 商品标题
                    if title == name:  # 校验商品名字是否相同
                        zk_final_price = couponResult[index].get("zk_final_price", 0.00)  # 商品售价
                        coupon_info = couponResult[index].get("coupon_info", "")  # 优惠券信息
                        coupon_share_url = couponResult[index].get("coupon_share_url", "")  # 优惠券连接
                        couponInfo += f"\n\n商品名称: {title}\n价格：{zk_final_price}\n优惠券：{coupon_info}\n优惠券链接：http:{coupon_share_url}"
                    else:
                        return TBKParams.ERROR_INFO
                print(couponData + couponInfo)
                return couponData + couponInfo
            elif resp and "error_response" in resp:
                print("", resp)
                return TBKParams.ERROR_INFO
            else:
                print("未知错误", resp)
                return TBKParams.ERROR_INFO
        except Exception as e:
            print("错误", e)
            return TBKParams.ERROR_INFO