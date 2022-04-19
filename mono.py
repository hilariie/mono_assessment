import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer


def text_process(text):
    """
    Cleans and preprocesses text
    :param text:
    :return text: :type str
    """
    stop_words = stopwords.words("english")
    lem = WordNetLemmatizer()
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.split()
    text = [lem.lemmatize(word.lower()) for word in text if not word in stop_words]
    text = " ".join(text)
    return text


def transaction_grouping(response_list):
    """
    Groups transactions based on transaction narration
    :param response_list: list of dictionary containing transaction data :type list
    :return: grouped transactions along side average number of days between transactions for each group
    """
    narr_list = []  # list to hold narrations used for display
    narration_list = []  # list to hold narrations used for training model
    amount_list = []  # list to hold amount
    type_list = []  # list to hold transaction type
    date_list = []  # list to hold transaction date
    for response in response_list:
        narr_list.append(response["narration"])
        # clean and preprocess narration before appending
        narration_list.append(text_process(response["narration"]))
        amount_list.append(response["amount"])
        type_list.append(response["type"])
        date_list.append(response["date"])

    x_transformed = TfidfVectorizer(analyzer=text_process,
                                    ngram_range=(1, 3)).fit_transform(narration_list)
    n_clusters = round(x_transformed.shape[0] / 3.2)
    model = KMeans(n_clusters=n_clusters, random_state=6)
    model.fit(x_transformed)
    df = pd.DataFrame({"narration": narr_list, "groups":model.labels_,
                       "amount": amount_list, "type": type_list,
                       "date": date_list})
    # print(df["groups"].groupby(df["narration"]).median()[:8])

    df2 = df.drop(["groups"], axis=1)

    # Getting grouped transactions as list of dictionaries and calculating average number of days btw transactions
    transactions_list = []  # list to hold grouped transaction dictionaries
    avg_days_list = []

    for m in range(n_clusters):
        temp_list = []  # list that holds transaction details before appended into transaction list
        date_list_2 = []  # list that holds dates in transactions before the mean is computed

        # Get the index of transactions with similar groups
        index = df[df["groups"] == m].index
        # loop through  index and append rows as dictionaries to list
        for n in index:
            temp_list.append(df2.iloc[n].to_dict())

        # loop through length of "temp_list" to get and calculate average days between transactions
        for i in range(len(temp_list)):
            # if loop is at the end, break becuase there is no subsequent date to compute difference.
            if i == max(range(len(temp_list))):
                break
            # convert first 10 strings which are dates
            d1 = datetime.strptime(temp_list[i]["date"][:10], "%Y-%m-%d")
            # loop through the remaining parts of temp_list to calculate differences between subsequent dates
            for ii in range(i+1, len(temp_list)):
                d2 = datetime.strptime(temp_list[ii]["date"][:10], "%Y-%m-%d")
                # break inner loop so we are left with the next immediate date
                break
            # append the differences in dates
            date_list_2.append(abs((d1 - d2).days))
        # if length of date_list_2 is empty due to groups with only one transactions \
        # (no second date to calculate differences in dates) append zero
        if len(date_list_2) == 0:
            date_list_2.append(0)
        # append the mean of the differences
        avg_days_list.append(round(np.mean(date_list_2)))
        # append list of dictionaries
        transactions_list.append(temp_list)

    # group transactions and average number of days between transactions in dictionary
    group_dict = {}
    for i  in range(len(avg_days_list)):
        group_dict[f"group{i+1}"] = {"average_number_of_days_between_transactions": avg_days_list[i],
                                     "transactions": transactions_list[i]}
    return group_dict


if __name__ == "__main__":
    response_list = [{"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./FBNMOBILE:CHUKWUMA HILARY AKPU/ND",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-04-16T03:55:29.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 47EDFF - 04/04/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-04-06T16:51:12.000Z"},
                     {"narration": "NIP/GTB/DUNKWU CHARLES ELOKA/tillJan REF701664587000003000002204032100",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-04-03T21:01:47.000Z"},
                     {"narration": "*ISO:MC Loc Web PYT Fee-004978803276--QTBPWSPTN/10117266/2220224707 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-04-03T20:19:36.000Z"},
                     {"narration": "MC Loc Web Pyt-004978803276--QTBPWSPTN/10117266/2220224707 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-04-03T20:19:36.000Z"},
                     {"narration": "NIP/FBN/CHINAZA EMMANUEL AKPU/USSD_CHINAZA EMMANUEL AKPU",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-04-03T18:37:58.000Z"},
                     {"narration": "SMS Notification Charge Mar 2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-27T14:27:29.000Z"},
                     {"narration": "2022 Qtr 1 MASTER Card Maintenance Fee",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-21T00:54:51.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 6D8713 - 02/03/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-11T15:31:15.000Z"},
                     {"narration": "Airtime//2349026638555//airtel",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-11T10:50:00.000Z"},
                     {"narration": "Airtime//2349026638555//airtel",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-09T21:57:48.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 0AB8D9 - 26/02/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-04T14:33:10.000Z"},
                     {"narration": "MC Loc POS Prch-007628751319--TEAMAPT LIMITED MONIEPO795 2070N908 NG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-03-01T13:47:03.000Z"},
                     {"narration": "SMS Notification Charge Feb 2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-27T13:09:41.000Z"},
                     {"narration": "NEFT IFO EMMANUELLA CHIDERA OKIKE",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-21T11:31:15.000Z"},
                     {"narration": "Transfer Charges",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-21T11:31:15.000Z"},
                     {"narration": "MC Loc Web Prch-007573306924--VICTORIA ISLAND VICTORIA ISLA NG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-21T06:26:47.000Z"},
                     {"narration": "TRF FRM CHUKWUMA HILARY AKPU TO |Balance Enquiry Charge",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-19T16:59:42.000Z"},
                     {"narration": "MC Loc POS Prch-000048007847--Shoprite Grand Towers LA LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-14T15:36:10.000Z"},
                     {"narration": "USSD Session Charge",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-13T15:06:50.000Z"},
                     {"narration": "NIP CR/FRIDAY JOHN/FBN",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-13T15:06:50.000Z"},
                     {"narration": "NIP Charge + VAT",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-13T15:06:50.000Z"},
                     {"narration": "STAMP DUTY CHARGE",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-12T22:48:14.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 24C906 - 04/02/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-10T16:09:24.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 1A5DB8 - 04/02/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-10T16:04:10.000Z"},
                     {"narration": "NIP/FBN/OBI ELVIS UCHECHUKWU/FBNMOBILE:CHUKWUMA HILARY AKPU/THANK YOU SO MUCH MAN",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-02-08T04:25:25.000Z"},
                     {"narration": "MC Loc POS Prch-000015012986--EMMY KITCHEN RESTAURANTFC LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-02-04T15:14:04.000Z"},
                     {"narration": "MC POS Intl- CARLETON GR APPLICATIO - 3BF101 - 30/01/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-31T16:47:45.000Z"},
                     {"narration": "SMS Notification Charge Jan 2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-30T10:15:01.000Z"},
                     {"narration": "STAMP DUTY CHARGE",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-29T23:20:59.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-01-29T11:56:00.000Z"},
                     {"narration": "MC Loc POS Prch-012930657667--TEAMAPT LIMITED MONIEP 246 207093CX NG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-29T10:24:53.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-01-28T20:18:27.000Z"},
                     {"narration": "*ISO:MC Loc Web PYT Fee-001965367544--QTBPWSPTN/10048079/2203969638 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-24T04:08:27.000Z"},
                     {"narration": "MC Loc Web Pyt-001965367544--QTBPWSPTN/10048079/2203969638 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-24T04:08:27.000Z"},
                     {"narration": "*ISO:MC Loc Web PYT Fee-001965359344--QTBPWSPTN/10048074/2203969438 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-24T04:08:25.000Z"},
                     {"narration": "MC Loc Web Pyt-001965359344--QTBPWSPTN/10048074/2203969438 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-24T04:08:25.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-01-24T04:08:11.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 4AFECF - 06/01/2022",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-10T14:58:58.000Z"},
                     {"narration": "STAMP DUTY CHARGE",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-08T23:03:26.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUEBUKA MCELVIS/FBNMOBILE:CHUKWUMA HILARY AKPU/NONE",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-01-06T19:50:18.000Z"},
                     {"narration": "USSD Session Charge",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-06T11:56:38.000Z"},
                     {"narration": "NIP CR/AKPU CHUKWUMA HILARY JNR./FBN",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-06T11:56:38.000Z"},
                     {"narration": "NIP Charge + VAT",
                      "amount": 000,
                      "type": "debit",
                      "date": "2022-01-06T11:56:38.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2022-01-06T11:01:34.000Z"},
                     {"narration": "*ISO:MC Loc Web PYT Fee-001831092535--QTBPWSPTN/10022079/2194697837 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-30T17:36:49.000Z"},
                     {"narration": "MC Loc Web Pyt-001831092535--QTBPWSPTN/10022079/2194697837 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-30T17:36:49.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-12-28T11:37:55.000Z"},
                     {"narration": "SMS Notification Charge Dec 2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-27T13:51:09.000Z"},
                     {"narration": "2021 Qtr 4 MASTER Card Maintenance Fee",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-27T01:22:43.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - B96726 - 11/12/2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-13T16:04:57.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - B95627 - 11/12/2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-13T15:28:01.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 9FA477 - 10/12/2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-13T15:19:06.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-12-10T09:00:32.000Z"},
                     {"narration": "*ISO:MC Loc Web PYT Fee-001677017824--QTBPWSPEC/15274901/2189436036 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-03T10:48:19.000Z"},
                     {"narration": "MC Loc Web Pyt-001677017824--QTBPWSPEC/15274901/2189436036 LANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-12-03T10:48:19.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-12-03T09:48:40.000Z"},
                     {"narration": "Capitalized Interest Credit",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-11-30T22:52:30.000Z"},
                     {"narration": "SMS Notification Charge Nov 2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-11-28T09:35:05.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - 390DDD - 17/11/2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-11-19T17:48:19.000Z"},
                     {"narration": "NIP/FBN/AKPU CHUKWUMA HILARY JNR./USSD_AKPU CHUKWUMA HILARY JNR.",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-11-15T18:24:16.000Z"},
                     {"narration": "MC POS Intl- APPLE.COM/BILL - BB3AA4 - 04/11/2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-11-10T18:08:54.000Z"},
                     {"narration": "NIP/GTB/DUNKWU CHARLES ELOKADUNKWU CHARLES ELOKA/REF701664587000001500002111030503",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-11-03T05:03:26.000Z"},
                     {"narration": "Capitalized Interest Credit",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-10-31T22:57:15.000Z"},
                     {"narration": "MC Loc Web Prch-389263518959--01ESA20211029202112GECCwww.etranzactLANG-",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-10-29T20:30:28.000Z"},
                     {"narration": "NIP/FBN/CHINAZA EMMANUEL AKPU/FBNMOBILE:CHUKWUMA HILARY AKPU/TRANSFER",
                      "amount": 000,
                      "type": "credit",
                      "date": "2021-10-29T20:28:16.000Z"},
                     {"narration": "SMS Notification Charge Oct 2021",
                      "amount": 000,
                      "type": "debit",
                      "date": "2021-10-24T16:04:22.000Z"}]

    group = transaction_grouping(response_list)
    print(group)
