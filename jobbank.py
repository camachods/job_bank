import string
import os
from bs4 import BeautifulSoup
import sys
import urllib2
import MySQLdb

reload(sys)
sys.setdefaultencoding('latin-1')

if os.path.exists('errorLog.txt'):
    os.remove('errorLog.txt')

errorLog = open('errorLog.txt', 'w')
pagen = str(1)
link_base = "https://www.jobbank.gc.ca/"
link_page = "jobsearch/jobsearch?page="
link_page2 = "&d=50&sort=M&action=s1&searchstring=Canada&lang=en&sid=20"

headers = {}
headers['User-Agent'] = 'GoogleBot'
	
def run(link):
    pagen = 1
    if link is None:
        return
    for i in range (1, 3):

        soup = get_html(link_base + link_page + str(pagen) + link_page2)
        pagen = pagen + 1

        if soup is None:
            return

        jobs_name = soup.find(attrs={"class": "results-jobs"})

        for job_name in jobs_name.findAll(attrs={"class": "resultJobItem"}):
            if job_name is None:
                continue

            link = job_name.attrs['href']
            name = job_name.find(attrs={"class": "title"}).text
            get_data_child(link_base + link)

def get_data_child(link):

    soup = get_html(link)
    if soup is None:
        return
    data = soup.find(attrs={"class": "job-posting-details-body col-md-9"})
    name = data.h2.text.replace('\n ', '')
    date_post = data.find(attrs={"class": "date"}).text.replace('\n ', '')
    company = data.find(attrs={"class": "business"}).find(attrs={"class": "external"})
    
    if company is None:
        company = data.find(attrs={"class": "business"}).find('strong').text.replace('\n ', '')
        company = company.replace("'", "")
    else: 
        company = data.find(attrs={"class": "business"}).find(attrs={"class": "external"}).text.replace('\n ', '')
        company = company.replace("'", "")

    job_details = data.find(attrs={"class": "job-posting-detail-requirements"})
    
    if job_details is None:
        job_details = "not available"
    else: 
        job_details = job_details.text.replace('\n ', '')
        job_details = job_details.replace("'", "")


    
    #city = data.find(attrs={"class": "city"})

    city = ""
    salary = ""
    vacancy = ""
    terms = ""
    start_date = ""
    benefits = ""
    conditions = ""
    job_number = ""

    conn = ConnecDB()
    conn.autocommit(False)
    cursor = conn.cursor()

    count = 1

    insert = "INSERT INTO jobs (name, datepost, company, jobdetails, city, salary, vacancy, terms, startdate, benefits, conditions, jobnumber) VALUES ('%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

    for li in data.find(attrs={"class": "job-posting-brief colcount-lg-2"}).findAll('li'):

        if count == 1:
            city = li.find(attrs={"class": "city"})
            if city is None:
                city = "not available"
            else: 
            	city = city.text.replace('\n ', '')
            	city = city.replace("'", "")
        elif count == 2:
            salary = li.text.replace('\n ', '')
        elif count == 3:
            vacancy = li.text.replace('\n ', '')
        elif count == 4:
            terms = li.text.replace('\n ', '')
        elif count == 5:
            start_date = li.text.replace('\n ', '')
        elif count == 6:
            benefits = li.text.replace('\n ', '')
        elif count == 7:
            conditions = li.text.replace('\n ', '')
        elif count == 8:
            job_number = li.text.replace('\n ', '')

        count += 1
    #print job_details
    insert %= (name, date_post, company, job_details, city, salary, vacancy, terms, start_date, benefits, conditions, job_number)
    cursor.execute(insert)
    conn.commit()    
    print name

def ConnecDB():
    return MySQLdb.connect(host='localhost',port=3306,
                                       db='jobca',
                                       user='root',
                                       passwd='123456')

def get_html(link):
    request = urllib2.Request(link)
    return BeautifulSoup(urllib2.urlopen(request), "html.parser")

if __name__ == "__main__":
    run(link_base + "jobsearch/jobsearch?page=&d=50&sort=D&wid=bf&action=s0&fage=30&lang=en&sid=20")
