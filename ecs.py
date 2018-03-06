#!/usr/bin/python
# coding=utf-8
import json,commands,pprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import CreateInstanceRequest,DeleteInstanceRequest,StopInstanceRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest,DescribeInstancesRequest,DeleteImageRequest
from aliyunsdkecs.request.v20140526 import DescribeInstanceMonitorDataRequest
from aliyunsdkrds.request.v20140815 import DeleteDatabaseRequest,ModifySecurityIpsRequest,DescribeDBInstancePerformanceRequest,RestartDBInstanceRequest

class aliAPI():

    def __init__(self):
        # 阿里云ak/as
        AccessKey = 'key'
        AccessSecret = 'sercet'
        # 所在区域
        RegionId = 'cn-shenzhen'
        self.clt = AcsClient(AccessKey, AccessSecret, RegionId)

    def create_ecs(self):
        # 创建ECS最好结合最新官方API文档
        request = CreateInstanceRequest.CreateInstanceRequest()
        request.get_ResourceOwnerAccount()
        request.set_accept_format('json')
        request.set_ImageId('m-94kpp9tck')
        request.set_SecurityGroupId('sg-94zjqi6ui')
        # 服务器类型
        request.set_InstanceType('ecs.s2.large')
        request.set_InternetChargeType('PayByTraffic')
        request.set_InternetMaxBandwidthOut('10')
        # 设置镜像
        request.set_InstanceName('elastic_tmp')
        # 设置密码
        request.set_Password('123456')
        result = self.clt.do_action(request)
        return result

    def stop_ecs(self, ecsId):
        request = StopInstanceRequest.StopInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(ecsId)
        result = self.clt.do_action(request)
        return result

    def del_ecs(self, ecsId):
        request = DeleteInstanceRequest.DeleteInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(ecsId)
        result = self.clt.do_action(request)
        return result

    def start_ecs(self, ecsId):
        request = StartInstanceRequest.StartInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(ecsId)
        result = self.clt.do_action(request)
        return result

    def ecs_list(self):
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_PageSize('100')
        result = self.clt.do_action(request)
        return result

    def monitor_ecs(self,InstanceId,ST,NT):
        request = DescribeInstanceMonitorDataRequest.DescribeInstanceMonitorDataRequest()
        request.set_accept_format('json')
        request.set_InstanceId(InstanceId)
        request.set_StartTime(ST)
        request.set_EndTime(NT)
        request.set_Period(3600)
        result = self.clt.do_action(request)
        return result


    def del_img(self, imgId):
        request = DeleteImageRequest.DeleteImageRequest()
        request.set_accept_format('json')
        request.set_ImageId(imgId)
        result = self.clt.do_action(request)
        return result

    def drop_database(self,RDSname,DBname):
        request = DeleteDatabaseRequest.DeleteDatabaseRequest()
        request.set_accept_format('json')
        request.set_DBName(DBname)
        request.set_DBInstanceId(RDSname)
        result = self.clt.do_action(request)
        return result

    def IPArray_database(self,RDSname,IPArray):
        request = ModifySecurityIpsRequest.ModifySecurityIpsRequest()
        request.set_accept_format('json')
        request.set_SecurityIps(IPArray)
        request.set_DBInstanceId(RDSname)
        result = self.clt.do_action(request)
        return result

    def monitor_database(self,RDSname,KEY,ST,NT):
        request = DescribeDBInstancePerformanceRequest.DescribeDBInstancePerformanceRequest()
        request.set_accept_format('json')
        request.set_Key(KEY)
        request.set_DBInstanceId(RDSname)
        request.set_StartTime(ST)
        request.set_EndTime(NT)
        result = self.clt.do_action(request)
        return result

    def restart_database(self, RDSname):
        request = RestartDBInstanceRequest.RestartDBInstanceRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(RDSname)
        result = self.clt.do_action(request)
        return result

class ali_shell(object):

    API = aliAPI()

    def show_ecs(self, Host=None, IP=None, Status=None):

        show = []
        ecs_info = [(i['InstanceName'], i['InstanceId'], i['Cpu'], i['Memory'], i['PublicIpAddress']['IpAddress'],
                     i['InnerIpAddress']['IpAddress'], i['InternetMaxBandwidthOut'],i['ZoneId'], i['Status'])
                     for i in json.loads(self.API.ecs_list())['Instances']['Instance']]

        for hostName, hostID, hostCPU, hostMemory, hostPublicIP, hostInnerIP, hostMaxBandwidth, hostZone, hostStatus in ecs_info:
            try:
                publicIP = hostPublicIP[0]
                innerIP = hostInnerIP[0]
            except:
                publicIP = "无"
                innerIP = "无"

            if Host and hostName.find(Host) > -1:
                show.append((hostName, hostID, hostCPU, hostMemory, publicIP, innerIP, hostMaxBandwidth, hostZone, hostStatus))

            elif IP and (IP == publicIP or IP == innerIP):
                show.append((hostName, hostID, hostCPU, hostMemory, publicIP, innerIP, hostMaxBandwidth, hostZone, hostStatus))

            #elif Status and Status == hostStatus:
            #    show.append((hostName, hostID, hostCPU, hostMemory, publicIP, innerIP, hostMaxBandwidth, hostZone, hostStatus))

            elif any([Host,IP,Status]) is False:
                show.append((hostName, hostID, hostCPU, hostMemory, publicIP, innerIP, hostMaxBandwidth, hostZone, hostStatus))


        for hostInfo in show:
            print "主机别名: %s\n主机ID: %s\nCPU: %s Core\n内存: %s MB\n外网IP: %s\n内网IP: %s\n带宽: %s Mbps\n区域: %s\n状态: %s\n" %\
                  (hostInfo[0], hostInfo[1], hostInfo[2], hostInfo[3], hostInfo[4], hostInfo[5], hostInfo[6], hostInfo[7], hostInfo[8])


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print '''说明:
    -ha: 显示所有ECS主机  -h <主机别名>: 显示指定别名ECS主机  -p <主机IP>: 根据IP显示ECS主机
    -s <主机IP>:启动ECS主机  -ss <主机IP>:停止ECS主机 -rd :重启数据库 '''
    if len(sys.argv) >= 2:
        if sys.argv[1] == '-ha':
            ali_shell().show_ecs()
        elif sys.argv[1] == '-h':
            ali_shell().show_ecs(sys.argv[2])
        elif sys.argv[1] == '-p':
            ali_shell().show_ecs(IP=sys.argv[2])
        elif sys.argv[1] == '-s':
            print aliAPI().start_ecs(sys.argv[2])
        elif sys.argv[1] == '-ss':
            print aliAPI().stop_ecs(sys.argv[2])
        elif sys.argv[1] == '-d':
            print aliAPI().del_ecs(sys.argv[2])
        elif sys.argv[1] == '-rd':
            # 输入数据库ID
            print aliAPI().restart_database('数据库id')
