import pandas as pd
import re
import time
import pickle
import requests

# lxml must be installed but not imported

base_bug_url = "https://bugs.eclipse.org/bugs/show_bug.cgi?id="
base_history_url = "https://bugs.eclipse.org/bugs/show_activity.cgi?id="

timestamp = time.time()
# ------------------------------------- import, parse, and process data -----------------------------------------------

with open('bug_list_total.txt', newline='') as f:
    bug_id_list_total = [int(bug_id.strip()) for bug_id in f.readlines()]

# infile = open("refact_bug_list_scraped", 'rb')
# bug_id_list = pickle.load(infile)
# infile.close()

bug_list = []
reject_list = []
i = 0

for bug_id_val in bug_id_list_total:
    i += 1
    try:
        single_bug_data = pd.read_html(requests.get(base_bug_url + str(bug_id_val)).text)

        print(i, ":", bug_id_val)
        single_bug_data_created = str(single_bug_data[0][2])
        single_bug_data = single_bug_data[1].T

        change_codes = ["UNCONFIRMED", "CONFIRMED", "IN_PROGRESS", "RESOLVED", "VERIFIED", "FIXED", "INVALID",
                        "WONTFIX", "DUPLICATE", "WORKSFORME", "REOPENED"]

        change_date_dict = [
            ("CREATED", re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} \w{3}', single_bug_data_created).group())]

        temp_dict = {"bug_id": int(bug_id_val),
                     "status_res": single_bug_data[0][1],
                     "status": single_bug_data[0][1].split()[0],
                     "resolution": single_bug_data[0][1].split()[1] if len(single_bug_data[0][1].split()) > 1 else None,
                     "priority": single_bug_data[10][1].split()[0],
                     "depends_on": single_bug_data[19][1] if str(single_bug_data[19][1]) not in "nan" else None,
                     "blocks": single_bug_data[20][1] if str(single_bug_data[20][1]) not in "nan" else None,
                     "UNCONFIRMED": None,
                     "CONFIRMED": None,
                     "IN_PROGRESS": None,
                     "RESOLVED": None,
                     "VERIFIED": None,
                     "FIXED": None,
                     "INVALID": None,
                     "WONTFIX": None,
                     "DUPLICATE": None,
                     "WORKSFORME": None,
                     "REOPENED": None}

        try:
            single_bug_history = pd.read_html(requests.get(base_history_url + str(bug_id_val)).text)
            single_bug_history = single_bug_history[0].values.tolist()

            for entry in single_bug_history:
                change_date_dict.append((entry[-1], entry[1], entry[0]))
                if entry[-1] in change_codes:
                    temp_dict[entry[-1]] = entry[1]

            temp_dict.update({"created": change_date_dict[0][1],
                              "first_modified": change_date_dict[1][1] if len(change_date_dict) > 1 else None,
                              "last_modified": change_date_dict[-1][1] if len(change_date_dict) > 1 else None,
                              "last_modified_author": change_date_dict[-1][2] if len(change_date_dict) > 1 else None,
                              "full_change_list": change_date_dict})

            bug_list.append(temp_dict)

        except:
            print(i, ": \t ---> ", bug_id_val, "could not reach bug history")
            bug_list.append(temp_dict)
            continue

    except:
        reject_list.append(str(bug_id_val))
        print(i, ": \t ---> ", bug_id_val, "could not reach bug info")
        continue

# ------------------------------------------------- Pickle Data --------------------------------------------------------
outfile = open("scraped_bug_data", 'wb')
pickle.dump(bug_list, outfile)
outfile.close()

outfile = open("scraped_reject_bugs", 'wb')
pickle.dump(reject_list, outfile)
outfile.close()

print("\n\n-------- done. --------")
print("rejects: ", len(reject_list), "\n", reject_list)
print("time: ", time.time() - timestamp)
