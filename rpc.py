# -*- coding: utf-8 -*-
import telnetlib
_author_ = 'luwt'
_date_ = '2021/10/26 18:19'


# 创建telnet类对象
conn = telnetlib.Telnet()
# 连接dubbo接口地址
conn.open('localhost', '20883')
#1.cmd命令格式: 接口全名字.方法名(参数1，参数2，参数3...参数n)  2.write方法就是通过telnet发起dubbo请求，参数和单独使用telnet一致
# cmd = 'com.tqmall.venus.service.common.DemandRemoteService.page2Seller({"companyName":"北京京东公司技术测试林男","demandChannelType":2,"demandSn":"","gmtCreateEnd":1635350399000,"gmtCreateStart":1632672000000,"mobile":"","offerStatus":2,"orderColumn":"gmt_create","pageNo":1,"pageSize":20,"sellerId":60021852,"shopNameLike":"北京京东公司技术测试林男"})'
# cmd2 = 'com.tqmall.venus.service.common.OrderExternalMappingService.testDemand("北京京东公司技术测试林男")'
# cmd = 'org.demo.service.RpcTestService.testRpc()'
# cmd3 = 'org.demo.service.RpcTestService.testRpcArgs(1, "中间", "测试消息")'
# cmd4 = 'org.demo.service.RpcTestService.testRpcParams({"id": 1, "name": "中间的", "message": "测试的消息"})'
param = '{"goodsEntryList":[{"goodsId":65158670,"leagueId":78},{"goodsId":65158671,"leagueId":78}],"sellerId":60021871},'
cmd5 = f'com.tqmall.tqmallstall.service.combo.GoodsInfoService.getDemandGoodsInfoList({param})'
conn.write('invoke {}\n'.format(cmd5).encode())
# conn.write('ls -l org.demo.service.RpcTestService\n'.encode())
# 获取telnet返回信息
data = conn.read_until('dubbo>'.encode()).decode()
conn.close()
print(data)
