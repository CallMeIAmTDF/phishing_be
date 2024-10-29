import ipaddress
import json
import re
import urllib.request
from bs4 import BeautifulSoup
import socket
import requests
from googlesearch import search
import whois
from datetime import datetime, date
import time
from dateutil.parser import parse as date_parse


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def generate_data_set(url):
    data_set = []
    # Converts the given URL into a standard format
    if not re.match(r"^https?", url):
        url = "http://" + url
    # Stores the response of the input URL
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        response = ""
        soup = -999
    # gets the domain from the input URL
    domain = re.findall(r"://([^/]+)/?", url)[0]
    if re.match(r"^www.", domain):
        domain = domain.replace("www.", "")
    # Requests all the information about the domain
    whois_response = whois.whois(domain)
    rank_checker_response = ""
    try:
        rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
            "name": domain
        })
    except:
        pass
    # gets the global rank of the website
    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
    except:
        global_rank = -1

    # feature 1.
    try:
        pattern = r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))"
        ips = [match[0] for match in re.findall(pattern, url)]
        data_set.append(-1)
        print("feature 1")
    except:
        data_set.append(1)
        print("feature 1")

    # feature 2.
    if len(url) < 54:
        data_set.append(1)
        print("feature 2")
    elif len(url) >= 54 and len(url) <= 75:
        data_set.append(0)
        print("feature 2")
    else:
        data_set.append(-1)
        print("feature 2")

    # feature 3.
    match = re.search('bit.ly|goo.gl|shorte.st|go2l.ink|x.co|ow.ly|t.co|tinyurl|tr.im|is.gd|cli.gs|'
                      'yfrog.com|migre.me|ff.im|tiny.cc|url4.eu|twit.ac|su.pr|twurl.nl|snipurl.com|'
                      'short.to|BudURL.com|ping.fm|post.ly|Just.as|bkite.com|snipr.com|fic.kr|loopt.us|'
                      'doiop.com|short.ie|kl.am|wp.me|rubyurl.com|om.ly|to.ly|bit.do|t.co|lnkd.in|'
                      'db.tt|qr.ae|adf.ly|goo.gl|bitly.com|cur.lv|tinyurl.com|ow.ly|bit.ly|ity.im|'
                      'q.gs|is.gd|po.st|bc.vc|twitthis.com|u.to|j.mp|buzurl.com|cutt.us|u.bb|yourls.org|'
                      'x.co|prettylinkpro.com|scrnch.me|filoops.info|vzturl.com|qr.net|1url.com|tweez.me|v.gd|tr.im|link.zip.net',
                      url)
    if match:
        data_set.append(-1)
        print("feature 3")
    else:
        data_set.append(1)
        print("feature 3")

    # feature 4.
    if re.findall("@", url):
        data_set.append(-1)
        print("feature 4")
    else:
        data_set.append(1)
        print("feature 4")

    # feature 5.
    list = [x.start(0) for x in re.finditer('//', url)]
    if list[len(list) - 1] > 7:
        data_set.append(-1)
        print("feature 5")
    else:
        data_set.append(1)
        print("feature 5")

    # feature 6.
    if re.findall(r"https?://[^\-]+-[^\-]+/", url):
        data_set.append(-1)
        print("feature 6")
    else:
        data_set.append(1)
        print("feature 6")

    # feature 7.
    if len(re.findall(".", url)) < 3:
        data_set.append(1)
        print("feature 7")
    elif len(re.findall(".", url)) == 4:
        data_set.append(0)
        print("feature 7")
    else:
        data_set.append(-1)
        print("feature 7")

    # feature 8.
    try:
        if response.text:
            data_set.append(1)
            print("feature 8")
        else:
            data_set.append(-1)
            print("feature 8")
    except:
        data_set.append(-1)
        print("feature 8")

    # feature 9.
    expiration_date = whois_response.expiration_date
    registration_length = 0
    try:
        expiration_date = min(expiration_date)
        today = time.strftime('%Y-%m-%d')
        today = datetime.strptime(today, '%Y-%m-%d')
        registration_length = abs((expiration_date - today).days)

        if registration_length / 365 <= 1:
            data_set.append(-1)
            print("feature 9")
        else:
            data_set.append(1)
            print("feature 9")
    except:
        data_set.append(-1)
        print("feature 9")

    # feature 10.
    if soup == -999:
        data_set.append(-1)
        print("feature 10")
    else:
        try:
            flag = 1
            for head in soup.find_all('head'):
                if flag == 0:
                    break
                for head.link in soup.find_all('link', href=True):
                    dots = [x.start(0) for x in re.finditer('.', head.link['href'])]
                    if url in head.link['href'] or len(dots) == 1 or domain in head.link['href']:
                        data_set.append(1)
                        flag = 0
                        print("feature 10")
                        break
                    else:
                        data_set.append(-1)
                        print("feature 10")
                        flag = 0
                        break
        except StopIteration:
            data_set.append(-1)
            print("feature 10 pass")

    # feature 11.
    try:
        port = domain.split(":")[1]
        if port:
            data_set.append(-1)
            print("feature 11")
        else:
            data_set.append(1)
            print("feature 11")
    except:
        data_set.append(1)
        print("feature 11")

    # feature 12.
    if re.findall(r"^https", domain):
        data_set.append(-1)
        print("feature 12")
    else:
        data_set.append(1)
        print("feature 12")

    # feature 13.
    i = 0
    success = 0
    if soup == -999:
        data_set.append(-1)
        print("feature 13")
    else:
        for img in soup.find_all('img', src=True):
            dots = [x.start(0) for x in re.finditer('.', img['src'])]
            if url in img['src'] or domain in img['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for audio in soup.find_all('audio', src=True):
            dots = [x.start(0) for x in re.finditer('.', audio['src'])]
            if url in audio['src'] or domain in audio['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for embed in soup.find_all('embed', src=True):
            dots = [x.start(0) for x in re.finditer('.', embed['src'])]
            if url in embed['src'] or domain in embed['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for iframe in soup.find_all('iframe', src=True):
            dots = [x.start(0) for x in re.finditer('.', iframe['src'])]
            if url in iframe['src'] or domain in iframe['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        try:
            percentage = success / float(i) * 100
            if percentage < 22.0:
                data_set.append(1)
                print("feature 13")
            elif ((percentage >= 22.0) and (percentage < 61.0)):
                data_set.append(0)
                print("feature 13")
            else:
                data_set.append(-1)
                print("feature 13")
        except:
            data_set.append(1)
            print("feature 13")

    # feature 14.
    percentage = 0
    i = 0
    unsafe = 0
    if soup == -999:
        data_set.append(-1)
        print("feature 14")
    else:
        for a in soup.find_all('a', href=True):
            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (
                    url in a['href'] or domain in a['href']):
                unsafe = unsafe + 1
            i = i + 1

        try:
            percentage = unsafe / float(i) * 100
            if percentage < 31.0:
                data_set.append(1)
                print("feature 14")
            elif ((percentage >= 31.0) and (percentage < 67.0)):
                data_set.append(0)
                print("feature 14")
            else:
                data_set.append(-1)
                print("feature 14")
        except:
            data_set.append(1)
            print("feature 14")

    # feature 15.
    i = 0
    success = 0
    if soup == -999:
        data_set.append(-1)
        print("feature 15")
    else:
        for link in soup.find_all('link', href=True):
            dots = [x.start(0) for x in re.finditer('.', link['href'])]
            if url in link['href'] or domain in link['href'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for script in soup.find_all('script', src=True):
            dots = [x.start(0) for x in re.finditer('.', script['src'])]
            if url in script['src'] or domain in script['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1
        try:
            percentage = success / float(i) * 100
            if percentage < 17.0:
                data_set.append(1)
                print("feature 15")
            elif ((percentage >= 17.0) and (percentage < 81.0)):
                data_set.append(0)
                print("feature 15")
            else:
                data_set.append(-1)
                print("feature 15")
        except:
            data_set.append(1)
            print("feature 15")

        # feature 16.
        for form in soup.find_all('form', action=True):
            if form['action'] == "" or form['action'] == "about:blank":
                data_set.append(-1)
                print("feature 16")
                break
            elif url not in form['action'] and domain not in form['action']:
                data_set.append(0)
                print("feature 16")
                break
            else:
                data_set.append(1)
                print("feature 16")
                break

    # feature 17.
    if response == "":
        data_set.append(-1)
        print("feature 17")
    else:
        if re.findall(r"[mail\(\)|mailto:?]", response.text):
            data_set.append(-1)
            print("feature 17")
        else:
            data_set.append(1)
            print("feature 17")

    # feature 18.
    if response == "":
        data_set.append(-1)
        print("feature 18")
    else:
        if response.text == "":
            data_set.append(-1)
            print("feature 18")
        else:
            data_set.append(1)
            print("feature 18")

    # feature 19.
    if response == "":
        data_set.append(-1)
        print("feature 19")
    else:
        if len(response.history) <= 1:
            data_set.append(1)
            print("feature 19")
        elif len(response.history) <= 4:
            data_set.append(0)
            print("feature 19")
        else:
            data_set.append(-1)
            print("feature 19")

    # feature 20.
    if response == "":
        data_set.append(-1)
        print("feature 20")
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            data_set.append(-1)
            print("feature 20")
        else:
            data_set.append(1)
            print("feature 20")

    # feature 21.
    if response == "":
        data_set.append(-1)
        print("feature 21")
    else:
        if re.findall(r"event.button ?== ?2", response.text):
            data_set.append(1)
            print("feature 21")
        else:
            data_set.append(-1)
            print("feature 21")

    # feature 22.
    if response == "":
        data_set.append(-1)
        print("feature 22")
    else:
        if re.findall(r"alert\(", response.text):
            data_set.append(-1)
            print("feature 22")
        else:
            data_set.append(1)
            print("feature 22")

    # feature 23.
    if response == "":
        data_set.append(-1)
        print("feature 23")
    else:
        if re.findall(r"[<iframe>|<frameBorder>]", response.text):
            data_set.append(-1)
            print("feature 23")
        else:
            data_set.append(1)
            print("feature 23")

    # feature 24.
    if response == "":
        data_set.append(-1)
        print("feature 24")
    else:
        try:
            registration_date = \
                re.search(r"Creation Date:\s*(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}Z", whois_response.text).group(1)
            print({"Registration Date": registration_date})
            if diff_month(date.today(), date_parse(registration_date)) >= 6:
                data_set.append(1)
                print("feature 24")
            else:
                data_set.append(-1)
                print("feature 24")
        except Exception as e:
            data_set.append(1)


    # feature 25.
    dns = 1
    try:
        dns = whois.whois(domain)
    except:
        dns = -1
    if dns == -1:
        data_set.append(-1)
        print("feature 25")
    else:
        if registration_length / 365 <= 1:
            data_set.append(-1)
            print("feature 25")
        else:
            data_set.append(1)
            print("feature 25")

    # feature 26.
    u = (f"https://pro.similarweb.com/widgetApi/WebsiteOverview/WebRanks/SingleMetric?country=999&from=2024%7C09%7C01&to=2024%7C09%7C30&includeSubDomains=true&isWindow=false&keys={domain}&timeGranularity=Monthly&webSource=Total")
    try:
        data = json.loads(requests.get(u).text)
        first_key = next(iter(data))
        if data["Data"][first_key]["GlobalRank"]["Value"] < 100000:
            data_set.append(1)
            print("feature 26")
        else:
            data_set.append(0)
            print("feature 26")
    except Exception as e:
        print(e)
        data_set.append(-1)
        print("feature 26")

    # feature 27.
    try:
        if 0 < global_rank < 100000:
            data_set.append(-1)
            print("feature 27")
        else:
            data_set.append(1)
            print("feature 27")
    except:
        data_set.append(1)
        print("feature 27")

    # feature 28.
    site = search(url, 5)
    if site:
        data_set.append(1)
        print("feature 28")
    else:
        data_set.append(-1)
        print("feature 28")

    # feature 29.
    if response == "":
        data_set.append(-1)
        print("feature 29")
    else:
        number_of_links = len(re.findall(r"<a href=", response.text))
        if number_of_links == 0:
            data_set.append(-1)
            print("feature 29")
        elif number_of_links <= 2:
            data_set.append(0)
            print("feature 29")
        else:
            data_set.append(1)
            print("feature 29")
            # 30. Statistical_report
    url_match = re.search(
        r'at.ua|usa.cc|baltazarpresentes.com.br|pe.hu|esy.es|hol.es|sweddy.com|myjino.ru|96.lt|ow.ly', url)
    try:
        ip_address = socket.gethostbyname(domain)
        ip_match = re.search(
            r'146.112.61.108|213.174.157.151|121.50.168.88|192.185.217.116|78.46.211.158|181.174.165.13|46.242.145.103|121.50.168.40|83.125.22.219|46.242.145.98|'
            '107.151.148.44|107.151.148.107|64.70.19.203|199.184.144.27|107.151.148.108|107.151.148.109|119.28.52.61|54.83.43.69|52.69.166.231|216.58.192.225|'
            '118.184.25.86|67.208.74.71|23.253.126.58|104.239.157.210|175.126.123.219|141.8.224.221|10.10.10.10|43.229.108.32|103.232.215.140|69.172.201.153|'
            '216.218.185.162|54.225.104.146|103.243.24.98|199.59.243.120|31.170.160.61|213.19.128.77|62.113.226.131|208.100.26.234|195.16.127.102|195.16.127.157|'
            '34.196.13.28|103.224.212.222|172.217.4.225|54.72.9.51|192.64.147.141|198.200.56.183|23.253.164.103|52.48.191.26|52.214.197.72|87.98.255.18|209.99.17.27|'
            '216.38.62.18|104.130.124.96|47.89.58.141|78.46.211.158|54.86.225.156|54.82.156.19|37.157.192.102|204.11.56.48|110.34.231.42',
            ip_address)
        if url_match:
            data_set.append(-1)
            print("feature 30")
        elif ip_match:
            data_set.append(-1)
            print("feature 30")
        else:
            data_set.append(1)
            print("feature 30")
    except:
        print('Kindly check your internet connection.')

    print(data_set)
    return data_set