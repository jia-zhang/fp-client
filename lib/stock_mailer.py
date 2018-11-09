import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import datetime
from stock_util import StockUtil
from logger import Logger
import time

class StockMailer():
    def __init__(self):
        self.my_sender='3100820192@qq.com'    # 发件人邮箱账号
        self.my_pass = 'hymygengdhnydhfd'              # 发件人邮箱密码(当时申请smtp给的口令)
        self.date = datetime.datetime.now().strftime('%Y/%m/%d')
        self.rcpt_list = ["jenixe@126.com"]
        #self.rcpt_list = ["jenixe@126.com","286531599@qq.com","3797069@qq.com"]
        self.util = StockUtil()
        self.mail_server = '127.0.0.1'
        self.mail_port = 25
        self.logger = Logger("StockMailer")
        self.msg_body_list = []
    
    def add_msg_body(self,msg_str):
        self.msg_body_list.append(msg_str)
    
    def compose_msg_body(self,stock_list):
        self.add_msg_body('=======================')
        stock_status = "\n".join(self.util.get_summary_status_after_close(stock_list))
        self.msg_body_list.append(stock_status)
        self.add_msg_body('=======================\n')

    def send_fp_mail(self):
        today = self.util.get_today()
        msg_subject = "复盘结果"
        #stock_status = self.util.get_summary_status_after_close(stock_list)  
        print(type(self.msg_body_list))
        print(self.msg_body_list)  
        msg_body = "\n".join(self.msg_body_list)
        self.logger.info(msg_body)
        for rcpt in self.rcpt_list:
            self.logger.info("Sending mail to %s"%(rcpt))
            #self.send_mail_to_one_rcpt(rcpt,msg_subject,msg_body)
            self.send_mail_from_qq(rcpt,msg_subject,msg_body)
            time.sleep(10)
    
    def send_mail(self,rcpt_list):
        #for rcpt in rcpt_list:
        pass

    def send_mail_from_local(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz",self.my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP(self.mail_server,self.mail_port)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(self.my_sender, self.my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #print("aaabbb")
            ret=False
        return ret
    
    
    def send_mail_from_qq(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz",'3100820192@qq.com'])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login('3100820192@qq.com','hymygengdhnydhfd')  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #print("aaabbb")
            ret=False
        return ret

    def send_mail_from_gmail(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz","jenixg@gmail.com"])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.gmail.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login("jenixg@gmail.com", "trend#11")  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #print("aaabbb")
            ret=False
        return ret
    
    def send_mail_from_126(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz","jenixg@gmail.com"])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.126.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login("jenixe@126.com", "trend1980")  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #print("aaabbb")
            ret=False
        return ret
    
    def send_mail_from_ses(self,rcpt,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz","jenixg@gmail.com"])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["whoareyou",rcpt])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("email-smtp.us-east-1.amazonaws.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login("AKIAJ2Z7MJOL6TNGN6QA", "AqCyiM2iMvMSxHwZbD/vsgIR0001RXodmfYSSjEOlqWx")  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,[rcpt,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #print("aaabbb")
            ret=False
        return ret

if __name__ == '__main__':
    t = StockMailer()
    t.send_mail_from_qq('jenixe@126.com','test','this is a test mail')


