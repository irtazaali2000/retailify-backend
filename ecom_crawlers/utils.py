import smtplib

# from_addr = 'no-reply@gobazzar.com'
# password='D3jhsjsh$@12#WD1',
# smtpserver='mail.gobazzar.com:2525'
from_addr = 'noreply7@ukdevelopmentservices.com'
password = "[#ytcTkL6EK$"
smtpserver = "mail.ukdevelopmentservices.com:2525"

def sendemail(from_addr,
              to_addr_list,
              cc_addr_list,
              subject,
              message,
              login=from_addr,
              password=password,
              smtpserver=smtpserver):
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    server.sendmail(from_addr, to_addr_list, message)
    server.quit()


def clean_val(val):
    return val.replace('\n', '').replace('\t', '').replace('\r', '').strip() if val else ''


def clean_money_str(val):
    return format(float(clean_val(val.replace(',', '').replace('AED', ''))), '.2f') if val else format(0.0, '.2f')


def get_noon_stock_availability(response):
    raw_stocks = response.css('div.first-subtitle1 ::text').extract()
    availability = [item.lower() for item in raw_stocks]
    available = 'add to cart' in availability
    if available:
        return available
    else:
        return available