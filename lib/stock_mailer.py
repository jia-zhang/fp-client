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
        self.rcpt_list = ["jenixe@126.com","286531599@qq.com","3797069@qq.com"]
        self.util = StockUtil()
        self.logger = Logger("StockMailer")
        self.msg_subject = "复盘结果" 
        self.msg_body = ''
    
    def compose_msg_body(self,stock_list):
        ret = []
        ret.append('=======================')
        sum_status = self.util.get_summary_status(stock_list)
        #print(sum_status)
        stock_status = "\n".join(sum_status)
        ret.append(stock_status)
        ret.append('=======================\n')
        msg_body = "\n".join(ret)
        self.msg_body = "%s\n%s"%(self.msg_body,msg_body)
        self.logger.info(msg_body)
        return msg_body

    def send_fp_mail(self,real_send=0):
        if real_send==0:
            return
        #for rcpt in self.rcpt_list.split(','):
        #self.logger.info("Sending mail to %s"%(rcpt))                
        self.send_mail_from_qq(self.msg_subject,self.msg_body)
    
    def send_mail_from_qq(self,msg_subject,msg_body):
        ret=True
        try:
            msg=MIMEText(msg_body,'plain','utf-8')
            msg['From']=formataddr(["jiazzz",'3100820192@qq.com'])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=','.join(self.rcpt_list)              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            self.logger.info("Sending mail to %s"%(msg['To']))
            msg['Subject']="%s-%s"%(msg_subject,self.date)                # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login('3100820192@qq.com','hymygengdhnydhfd')  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender,self.rcpt_list,msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret=False
        return ret

if __name__ == '__main__':
    t = StockMailer()
    stock_list = ['sz002472', 'sh600695', 'sh600462', 'sz002026', 'sz002856', 'sz000609', 'sz300659', 'sz002058', 'sh603106', 'sh603569', 'sh600846', 'sz002798', 'sz000971', 'sh600630', 'sz300234', 'sz300543', 'sz002328', 'sz002164', 'sz002226', 'sz300606', 'sz300636', 'sz002837', 'sh603165', 'sh600624', 'sz002417', 'sh603305', 'sh600283', 'sh600784', 'sz002680', 'sz300541', 'sz300651', 'sh603738', 'sz300607', 'sh603648', 'sh600366', 'sh600165', 'sh600355', 'sh603180', 'sz002288', 'sz002709', 'sh600278', 'sh600621', 'sz002492']
    t.compose_msg_body(stock_list)


