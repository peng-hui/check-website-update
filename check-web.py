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
        server.sendmail(FROM, TO, message.encode('utf-8'))
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

from html_similarity import structural_similarity
def similarity(str1, str2):
    return structural_similarity(str1, str2)

def check_web(url, title, data_dir):
    try:
        req = Request(url=url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'})
        req.add_header('Referer', url)
        with urlopen(req) as fp:
            new_content = fp.read().decode('utf-8')
            filePath = join(data_dir, title)
            diff = ''
            similar_score = 1.0

            if not exists(filePath):
                old_content = ""
                similar_score = 2
                # check a new website, we do not append the diff
            else:
                with open(filePath, 'r', encoding='utf-8') as data_fp:
                    old_content = data_fp.read()
                    with open("%s.bak" % filePath, 'w', encoding='utf-8') as backup_data_fp:
                        backup_data_fp.write(old_content)
                    similar_score = similarity(new_content, old_content)
                    diff = "\n".join(list(unified_diff(old_content.split('\n'), new_content.split('\n'))))
            with open(filePath, 'w', encoding='utf-8') as data_fp:
                # write latest version
                data_fp.write(new_content)
            return diff, similar_score
    except Exception as e:
        print(e)
        pass

    return '', 3

from datetime import datetime, date
import pathlib
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-t', '--threshold', type=float, required=True, help="Notificaton threshold in [0, 1].")
    parser.add_argument ('--mail', action='store_true', help="Alert check results over mails")
    args = parser.parse_args()

    file_dir = pathlib.Path(__file__).parent.resolve()
    data_dir = join(file_dir, "web-cache")
    if not exists(data_dir):
        os.mkdir(data_dir)
    with open(join(file_dir, 'urls.txt'), 'r') as fp:
        inputs = [i.strip() for i in fp.readlines() if not i.startswith('#')]
        urls = [item.split()[0] for item in inputs]
        titles = [item.split()[1] for item in inputs]
    diffs = []
    updatedUrls = []
    updatedTitles = []
    summary = ""
    for url, title in zip(urls, titles):
        diff, score = check_web(url, title, data_dir)
        summary += url + " " + title  + ": " + str(score) + "\n"
        #print('check %s, diff bytes %s, updated? (%f, %s)'% (title, str(len(diff)), score, str(1 - score > args.threshold)))
        if score < args.threshold: # similar-score below threshold
            diffs.append(diff)
            updatedUrls.append(url)
            updatedTitles.append(title)

    content = "=====UPDATES ON=====\n" + "---site---\n".join([updatedTitles[i] + "\n" +  diffs[i] for i in range(len(diffs))]) + "\n"
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

    if len(updatedUrls) > 0 and args.mail:
        mail_info= open(join(file_dir, 'mail_info.txt')).readlines()
        _user = mail_info[0].strip()
        _password = mail_info[1].strip()

        to = [i.strip() for i in mail_info[2:]]
        subject = 'Web Service Sync'
        ret = send_email(_user, _password, to, subject, content)

