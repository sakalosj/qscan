import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger('qualys.mail')


class Mail:
    def __init__(self, template='templates/finished_scan.html', attachment=None, failed_items=None, status=None):
        self._msgRoot = MIMEMultipart()
        self._msgRoot['From'] = 'qualysscan@dhl.com'
        self._template = template
        self._attachment = attachment
        self._failed_items = failed_items
        self._status = status or 'status missing'

    @property
    def to(self):
            return self._msgRoot['To']

    @to.setter
    def to(self, emailAddress):
        if self._validateEmailAddress(emailAddress):
            self._msgRoot['To'] = emailAddress

    @property
    def cc(self):
        return self._msgRoot['Cc']

    @cc.setter
    def cc(self, emailAddress):
        if self._validateEmailAddress(emailAddress):
            self._msgRoot['Cc'] = emailAddress

    @property
    def bcc(self):
        return self._msgRoot['Bcc']

    @bcc.setter
    def bcc(self, emailAddress):
        if self._validateEmailAddress(emailAddress):
            self._msgRoot['Bcc'] = emailAddress

    @property
    def subject(self):
        return self._msgRoot['Subject']

    @subject.setter
    def subject(self, subject):
        self._msgRoot['Subject'] = subject

    def _prepare_mail(self):

        with open(self._template) as html_template:
            msgBody = MIMEText(html_template.read().format(status=self._status, failed_info=self._failed_items,), 'html')
            self._msgRoot.attach(msgBody)

        if self._attachment:
            part = MIMEApplication(
                self._attachment,
                Name='report.csv'
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % 'report.csv'
            self._msgRoot.attach(part)

    def send(self):
        self._prepare_mail()
        try:
            smtp = smtplib.SMTP('localhost')
            smtp.send_message(self._msgRoot)
            smtp.quit()
        except Exception as e:
            logger.exception('Sending mail failed')

    def _validateEmailAddress(self, emailAddress):
        if True:
            return True
        else:
            logger.error("Email {} address is not valid - not added to TO field".format(emailAddress))