# Check updates on websites

## Preparation
0. `pip install -r requirements.txt`
1. `urls.txt` that specifies the urls you want to check. Each url starts a new line. You can use a sharp character to comment out specific urls.
```txt
https://google.com title-goole
# http://baidu.com  # comment out this url
```
2. `mail_info.txt` that specifies the information of sender and recipients for email notification.
```txt
sender@example.com
sender_password
recipient1@example.com
recipient2@example.com
...
```
Note that you might also need to change the corresponding SMTP server configuration for email notification, e.g., line 14.

## Run
You can specify a threshold to selectively enabling email notification only when the update on a website is significant enough. The threshold is expected to be a float in the range of [0, 1]. There is an optional `mail` option.
```bash
python3 check-web.py -t 0.01 --mail
```
You can add above command to `crontab` to periodically check updates.
