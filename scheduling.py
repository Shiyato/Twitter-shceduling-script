from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import googledrive, os
import pandas as pd

driver = Chrome('./chromedriver')
find_elem = lambda selector: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


def read_table(name='table.csv'):
    googledrive.download_document('table id', name, 'text/csv') #Past table id from google
    return pd.read_csv(name)


def find_differense(table1, table2):
    c = 0
    out = []
    list1 = [row for id, row in table1.iterrows()]
    list2 = [row for id, row in table2.iterrows()]
    for i in range(max(len(list1), len(list2))):
        try:
            row2 = [value for key, value in list2[i].items()]
        except:
            continue
        try:
            row1 = [value for key, value in list1[i].items()]
        except:
            c += 1
            out.append(row2)
            continue
        bl = False
        for j in range(len(row1)):
            if str(row1[j]) != str(row2[j]):
                bl = True
        if bl:
            out.append(row2)
    return out


def read_twitter_accounts(num=None):
    accounts = dict()
    with open('Twitter_accounts', 'r') as file:
        for line in file:
            if line:
                line = tuple(line.split(';'))
                accounts[line[0]] = line[1]
    return accounts


def login_account(username, password):
    driver.get('https://tweetdeck.twitter.com/')
    find_elem('a').click()
    find_elem('input[name="username"]').send_keys(username)
    find_elem('div[role="button"][tabindex="0"]:not([data-testid])').click()
    find_elem('input[name="password"]').send_keys(password)
    try:
        find_elem('div[role="button"][tabindex="0"][data-testid="LoginForm_Login_Button"]').click()
    except:
        pass


def logout_account():
    find_elem('a[data-action="settings-menu"]').click()
    find_elem('a[data-action="signOut"]').click()
    find_elem('div[role="button"][tabindex="0"][data-testid="confirmationSheetConfirm"]').click()


def schedule_tweet(text='', content='', hour='', minute='', daytime='', month='', year='', day=''):
    try:
        tweet_btn = find_elem('button.tweet-button:not([is-hidden])')
        tweet_btn.click()
    except:
        pass

    find_elem('textarea').send_keys(text)
    find_elem('button.js-schedule-button').click()
    am_pm = find_elem('#amPm')
    if am_pm.text != daytime.upper():
        am_pm.click()
    if len(hour) < 2:
        hour = '0' + hour
    find_elem('#scheduled-hour').send_keys(hour)
    find_elem('#scheduled-minute').send_keys(minute)
    month_year = find_elem('#caltitle').text.split()
    while month_year[0] != month.capitalize() or month_year[1] != year:
        find_elem('#next-month').click()
        month_year = find_elem('#caltitle').text.split()
        if month_year[1] > year:
            raise ValueError('Uncorrect date')
    find_elem(f'a[href="#{day}"]').click()
    if content:
        items = googledrive.main()
        if content in items[1]:
            ind = items[1].index(content)
            id, mtype = items[0][ind], items[2][ind]
            path = f'source_for_posts/{content}'
            googledrive.download_file(id, path)
            input_field = find_elem('input[type="file"]')
            input_field.send_keys(os.path.abspath(path))
        else:
            raise ValueError('No access to CONTENT on GoogleDrive')
    submit_field = find_elem('button.js-send-button').click()


def time_str_to_str(date, time):
    month, day, year = date.split('/')
    time, daytime = time.split()
    hour, minute = time.split(':')
    return [hour, minute, daytime, month, year, day]


def main():
    table = read_table()
    if 'old_table.csv' in os.listdir('./'):
        table = find_differense(table, pd.read_csv('old_table.csv'))
    else:
        table = find_differense(table, table)
    tweets_by_accounts = dict()

    for row in table:
        account = row.get('ACCOUNT')
        if account and account not in tweets_by_accounts.keys():
            tweets_by_accounts[account] = []
        tweets_by_accounts[account].append((row.get('MESSAGE'), row.get('HASHTAGS'), row.get('CONTENT'), row.get('DATE'), row.get('TIME')))
    accounts_login_data = read_twitter_accounts()

    for username, tweets in tweets_by_accounts.items():
        password = accounts_login_data[username]
        login_account(username, password)
        for tweet_data in tweets:
            time = time_str_to_str(tweet_data[3], tweet_data[4])
            schedule_tweet(tweet_data[0] + '\n\n' + tweet_data[1], tweet_data[2], time[0], time[1], time[2], time[3], time[4], time[5])
        logout_account()
    driver.close()


def test():
    driver.close()
    tb1 = pd.read_csv('test_table.csv')
    tb2 = read_table('table.csv')


if __name__ == '__main__':
    main()
