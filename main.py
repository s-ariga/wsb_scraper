import praw
import re
import pandas as pd
import config


def get_stock_list():
    ticker_dict = {}
    filelist = ["list1.csv", "list2.csv", "list3.csv"]
    for file in filelist:
        tl = pd.read_csv(file, skiprows=0, skip_blank_lines=True)
        tl = tl[tl.columns[0]].tolist()
        for ticker in tl:
            ticker_dict[ticker] = 1
    return ticker_dict


def get_prev_tickers():
    prev = open("prev.txt", "w+")
    prev_tickers = prev.readlines()
    prev_tickers = [x.strip() for x in prev_tickers]
    return prev, prev_tickers


def get_tickers(sub, stock_list):
    reddit = praw.Reddit(
        client_id=config.api_id,
        client_secret=config.api_secret,
        user_agent="WSB Scraping",
    )
    prev, prev_tickers = get_prev_tickers()
    weekly_tickers = {}

    regex_pattern = r'\b([A-Z]+)\b'
    ticker_dict = stock_list
    blacklist = ["A", "I", "DD", "WSB", "YOLO", "RH", "EV"]
    for submission in reddit.subreddit(sub).top("week"):
        strings = [submission.title]
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            strings.append(comment.body)
        for s in strings:
            for phrase in re.findall(regex_pattern, s):
                if phrase not in blacklist:
                    if ticker_dict.get(phrase) == 1:
                        if weekly_tickers.get(phrase) is None:
                            weekly_tickers[phrase] = 1
                        else:
                            weekly_tickers[phrase] += 1
    top_tickers = sorted(weekly_tickers, key=weekly_tickers.get, reverse=True)[:5]
    top_tickers = [ticker + '\n' for ticker in top_tickers]

    to_buy = []
    to_sell = []
    for new in top_tickers:
        if new not in prev_tickers:
            to_buy.append(new)
    for old in prev_tickers:
        if old not in top_tickers:
            to_sell.append(old)

    prev.writelines(top_tickers)
    prev.close()
    write_to_file(sub+'.txt', to_buy, to_sell)


def write_to_file(file, to_buy, to_sell):
    f = open(file, "w")
    f.write("BUY:\n")
    f.writelines(to_buy)
    f.write("\nSELL:\n")
    f.writelines(to_sell)
    f.close()


def main():
    subs = ["wallstreetbets", "stocks", "investing", "smallstreetbets"]
    stock_list = get_stock_list()
    for sub in subs:
        get_tickers(sub, stock_list)


if __name__ == '__main__':
    main()
