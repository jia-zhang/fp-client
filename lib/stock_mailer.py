import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import datetime
from stock_util import StockUtil
from logger import Logger

class StockMailer():
    def __init__(self):
        self.my_sender='3100820192@qq.com'    # 发件人邮箱账号
        self.my_pass = 'hymygengdhnydhfd'              # 发件人邮箱密码(当时申请smtp给的口令)
        self.date = datetime.datetime.now().strftime('%Y_%m_%d')
        #self.rcpt_list = "286531599@qq.com,jenixe@126.com"
        self.rcpt_list = "jenixe@126.com"
        self.util = StockUtil()
        self.logger = Logger("StockMailer")

    def send_fp_mail(self,stock_list):
        today = self.util.get_today()
        msg_subject = "%s 复盘结果"%(today)
        stock_status = self.util.get_summary_status_after_close(stock_list)    
        msg_body = stock_status.join("\n")
        self.logger.info(msg_body)
        for rcpt in self.rcpt_list:
            self.send_mail_to_one_rcpt(rcpt,msg_subject,msg_body)
    
    def send_mail(self,rcpt_list):
        #for rcpt in rcpt_list:
        pass
    
    def send_mail_to_one_rcpt(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz",self.my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(self.my_sender, self.my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print("aaabbb")
            ret=False
        return ret


