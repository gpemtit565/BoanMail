#보안 공지 메일

import smtplib
import requests
from bs4 import BeautifulSoup as bs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

old_links = []

def load_old_links():

    global old_links
    try:
        with open("list.txt", "r", encoding="utf-8") as file:
            old_links = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("list.txt 파일이 존재하지 않음")
        old_links = []

def get_new_links(old_links): #new link를 만들어줌

    url = "https://www.boho.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
    html = requests.get(url)
    soup = bs(html.text, "html.parser")

    myurls = soup.find_all(class_='sbj tal')
    myurls_text = []  # myurls_text 리스트 초기화


    for myurl in myurls:
        # 각 myurl에서 'a' 태그를 찾아 'href' 속성을 추출
        a_tag = myurl.find('a')  # 'a' 태그 찾기
        if a_tag and 'href' in a_tag.attrs:  # 'href' 속성이 있는지 확인
            href = a_tag['href']
            myurls_text.append('https://www.boho.or.kr/'+href)
    
    new_links = [link for link in myurls_text if link not in old_links]

    return new_links

def save_links():

    global old_links

    load_old_links()

    new_links = get_new_links(old_links)

    if new_links:
        with open("list.txt", "a", encoding="utf-8") as file:
            for link in new_links:
                file.write(link + "\n")
                print("save")
    else:
        print("no new links")

    old_links += new_links.copy()

    return old_links

def mailheader(new_link):
    h2_texts = []

    for url in new_link:
        html = requests.get(url)
        soup = bs(html.text, "html.parser")

        myurls = soup.find_all(class_='b_title') # b_title 클래스 찾기

        for myurl in myurls:
            h2_tag = myurl.find('h2')  # b_title 클래스에서 'h2' 태그 찾기
            h2_text = h2_tag.get_text(strip=True)
            h2_texts.append(h2_text)

    return h2_texts

def mailbody(new_link):
    
    body_text = []

    for url in new_link:
        html = requests.get(url)
        soup = bs(html.text, "html.parser")

        myurls = soup.find_all(class_='content_html')
        # body_text.append(soup.find_all(class_='content_html'))

        for myurl in myurls:
            body_text.append(str(myurl))
        #     p_text = myurl.get_text(strip=True)
        #     body_text.append(f"<p>{p_text}</p><br>")

    return body_text

load_old_links() # 구 링크 로드


if __name__ == '__main__':

    # 새로운 링크 가져오기
    new_link = get_new_links(old_links)
    save_links()
    print("Final new links:", new_link)    
    
    if not new_link:
        print("뉴스가 없다")
    else:
        load_dotenv('mail.env')

        mail_header = mailheader(new_link)
        # print('test', mail_header)
        mail_body = mailbody(new_link)
        # print('test2', mail_body)

        # for i in range(len(new_link)):
        #     subject = mail_header[i]
        #     body = mail_body[i]
        for subject,body in zip(mail_header, mail_body):
            # env파일에 기입
            sender = os.getenv('SENDER_EMAIL')
            receiver = os.getenv('RECEIEVE_EMAIL').split(',')
            app_password = os.getenv('APP_PASSWORD')

            title = f"보안 메일 : {subject}"
            content = f"{body}"

            msg = MIMEMultipart()
            msg.attach(MIMEText(content, "html", _charset="utf-8"))
            msg['Subject'] = title


            # 세션 생성
            with smtplib.SMTP('smtp.gmail.com', 587) as s:
            # TLS 암호화
                s.starttls()

                # 로그인 인증과 메일 보내기
                s.login(sender, app_password)
                
                print(f"from : {sender}")
                print(f"To: {','.join(receiver)}")
                print("Message content:")
                print(msg.as_string())

                s.sendmail(sender, receiver, msg.as_string())
                print("Email sent successfully")
