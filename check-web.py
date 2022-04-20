#!/usr/local/bin/python3
import smtplib
import socks
def send_email(user, pwd, recipient, subject, body):
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.yeah.net", 25)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
        return True
    except Exception as e:
        print ("failed to send mail", e)
        return False

from urllib.parse import quote
from urllib.request import urlopen, Request
from os.path import join, exists
from difflib import SequenceMatcher, unified_diff
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from html_similarity import similarity, structural_similarity
def similarity(str1, str2):
    return structural_similarity(str1, str2)

def check_web(url, data_dir):
    try:
        req = Request(url=url, headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        req.add_header('Referer', url)
        with urlopen(req) as fp:
            new_content = fp.read().decode('utf-8')
            filePath = join(data_dir, quote(url, safe=''))
            diff = False
            similar_score = 1.0

            if not exists(filePath):
                old_content = ""
                similar_score = 2
                # check a new website, we do not append the diff
            else:
                with open(filePath, 'r') as data_fp:
                    old_content = data_fp.read()
                    with open("%s.bak" % filePath, 'w') as backup_data_fp:
                        backup_data_fp.write(old_content)
                    similar_score = similarity(new_content, old_content)
                    diff = "\n".join(list(unified_diff(old_content.split('\n'), new_content.split('\n'))))
            with open(filePath, 'w') as data_fp:
                # write latest version
                data_fp.write(new_content)
            return diff, similar_score
    except Exception as e:
        print(e)
        pass

    return False, 3

from datetime import datetime, date
import pathlib
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-t', '--threshold', type=float, required=True, help="Notificaton threshold in [0, 1].")
    args = parser.parse_args()

    file_dir = pathlib.Path(__file__).parent.resolve()
    data_dir = join(file_dir, "web-cache")
    if not exists(data_dir):
        os.mkdir(data_dir)
    with open(join(file_dir, 'urls.txt'), 'r') as fp:
        urls = [i.strip() for i in fp.readlines() if not i.startswith('#')]
    diffs = []
    updatedUrls = []
    summary = ""
    for url in urls:
        diff, score = check_web(url, data_dir)
        summary += url + ": " + str(score) + "\n"
        print('check %s, updated? %s, %f'% (url, 'False' if diff == False else 'True', score))
        if 1 - score > args.threshold: # there is significant diff above threshold
            diffs.append(diff)
            updatedUrls.append(url)

    content = "=====UPDATES ON=====\n" + "\t".join(updatedUrls) + "\n=====DETAILS=====\n" + "\n".join(diffs)
    if len(updatedUrls) > 0:
        mail_info= open(join(file_dir, 'mail_info.txt')).readlines()
        _user = mail_info[0].strip()
        _password = mail_info[1].strip()

        to = [i.strip() for i in mail_info[2:]]
        subject = 'Web Service Sync'
        ret = send_email(_user, _password, to, subject, content)

    if not exists(join(data_dir, 'web-check.log')):
        open(join(data_dir, 'web-check.log'), 'w').close()
    with open(join(data_dir, 'web-check.log'), 'r+') as fp:
        today = date.today()
        old_content = fp.read()
        fp.seek(0)
        fp.write("\n-------%s------\n" % today.strftime("%d/%m/%Y"))
        fp.write(summary)
        fp.write(content)
        fp.write(old_content)
