import pickle
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from brokenaxes import brokenaxes
import matplotlib.pyplot as plt
from matplotlib import ticker
from pandas.core import nanops

# # pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)
#
# infile = open("scraped_bug_data", 'rb')
# bug_list = pickle.load(infile)
# infile.close()
#
#
# # make return time in days
# def date_diff(date_one, date_two):
#     # """returns the difference between two timestamps IN DAYS as a string"""
#     t_d = (datetime.strptime(date_two[:10], '%Y-%m-%d').timestamp() -
#            datetime.strptime(date_one[:10], '%Y-%m-%d').timestamp()) / 86400
#     return t_d if t_d >= 0 else np.NaN
#
#
# def make_hyperlink(v):
#     url = "https://bugs.eclipse.org/bugs/show_bug.cgi?id={}"
#     return '=HYPERLINK("%s", "%s")' % (url.format(v), v)
#
#
# # ------------------------------------------------- Create DF ----------------------------------------------------------
#
# # df.append() creates a new df each time, we use dicts instead then mass convert to DataFrame
# bug_df = pd.DataFrame(bug_list)
# bug_df = bug_df.replace({None: np.NaN})
#
# bug_df['time_passed_touch'] = bug_df.apply(
#     lambda x: date_diff(x['created'], x['first_modified']) if x['first_modified'] is not np.NaN else np.NaN, axis=1)
#
# lst = ['RESOLVED', 'VERIFIED', 'CLOSED']
#
# bug_df['time_passed_last'] = bug_df.apply(
#     lambda x: date_diff(x['created'], x['last_modified']) if x['last_modified'] \
#                                                              is not np.NaN and x['status'] in lst else np.NaN, axis=1)
#
# bug_df['bug_id'] = bug_df['bug_id'].apply(lambda x: make_hyperlink(x))
#
# bug_df.to_excel("bug_data.xlsx")

# At this point, the bug_data.xlsx was manually reviewed for incorrect bugs.
# The bug_data.xlsx that exists in this folder is the reviewed dataset.


# ------------------------------------------------- Analyze DF ---------------------------------------------------------

bug_df = pd.read_excel('bug_data.xlsx')
total_bugs = bug_df.count()
print("Counts of Statuses in Full DB: \n", bug_df["status"].value_counts(dropna=False))
print("\nCounts of Resolutions in Full DB: \n", bug_df["resolution"].value_counts(dropna=False))

print(bug_df.count())

res_df = bug_df[bug_df.status == 'RESOLVED'].append(
    bug_df[bug_df.status == 'CLOSED']).append(bug_df[bug_df.status == 'VERIFIED'])
print("\nCounts of Resolutions in Resolved DB: \n", res_df["resolution"].value_counts(dropna=False))

# nanops.nansum ignores null values, just like .count()
touch_total = nanops.nansum(bug_df['time_passed_touch'])
touch_count = bug_df['time_passed_touch'].count()

res_total = nanops.nansum(res_df['time_passed_last'])
res_count = res_df['time_passed_last'].count()

print("\ntouch_c: ", touch_count, " touch_t: ", touch_total, " avg: ", touch_total / touch_count)
print("res_c: ", res_count, " res_t: ", res_total, " avg: ", res_total / res_count)

touch_df = bug_df[bug_df.time_passed_touch.notnull()]
print("\ntouch_df count: \n", touch_df.count())

# Create subset with authors 'genie' and 'webmaster'
genie_df = bug_df[bug_df.last_modified_author == 'genie'] \
    .append(bug_df[bug_df.last_modified_author == 'webmaster'])
print("\ngenie/webmaster resolved bugs: \n", genie_df.count())
print("\ngenie_df largest time_passed_last: \n", genie_df.nlargest(10, 'time_passed_last'))
print("\nCounts of Resolutions in Genie DB: \n", genie_df["resolution"].value_counts(dropna=False))

# Create WONTFIX
wontfix_df = bug_df[bug_df.resolution == 'WONTFIX']
print("\nCounts of Authors in WONTFIX DB: \n", res_df["last_modified_author"].value_counts(dropna=False))

# Create subset w/o WONTFIX bugs
without_wontfix_df = bug_df
cond = without_wontfix_df['bug_id'].isin(wontfix_df['bug_id'])
without_wontfix_df.drop(without_wontfix_df[cond].index, inplace=True)

# Calculate and output rates
print("WONTFIX total: ", wontfix_df.count(), " WONTFIX rate: ", wontfix_df.count() / total_bugs)
print("RESOLVED total: ", res_df.count(), " RESOLVED rate: ", res_df.count() / total_bugs)
duplicate_count = bug_df[bug_df.resolution == 'DUPLICATE'].count()
print("DUPLICATE total: ", duplicate_count, " DUPLICATE rate: ", duplicate_count / total_bugs)

# ---------------------------------------------- Print Graphics --------------------------------------------------------

# print("\n\n", bug_df.groupby('status')['bug_id'].nunique())
# print("\n\n", bug_df.groupby('resolution')['bug_id'].nunique())

print("touch_largest: \n", bug_df.nlargest(15, 'time_passed_touch'))
print("resolve_largest: \n", bug_df.nlargest(15, 'time_passed_last'))

# BrokenAxes Trial
# fig = plt.figure(figsize=(5, 2))
# bax = brokenaxes(ylims=((0, 35), (4000, 5000)), hspace=.05)
# x = np.linspace(0, 1, 100)
# bax.plot(touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60))
# bax.set_xlabel('Time Passed (Days)')
# bax.set_ylabel('Count of Bugs')

# Broken Axis Histogram Submitted -> First Modified
plt.subplot(4, 1, 1)
ax1 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60)
ax1.set_ylim(4000, 5000)
ax1.spines['bottom'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)
ax1.set_facecolor("lightgrey")
ax1.set_ylabel("")
plt.title("Days Before a Bug is Modified")
plt.subplot(4, 1, (2, 4))
ax3 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60)
ax3.set_ylim(0, 35)
ax3.spines['top'].set_visible(False)
ax3.xaxis.tick_bottom()
ax3.set_facecolor("lightgrey")
ax3.set_ylabel("")
plt.xlabel("Time Passed (Days)")
plt.ylabel("Count of Bugs")
plt.savefig("graphics/time_touch_hist.pdf", bbox_inches='tight')
# plt.show()

# Broken Axis Histogram Submitted -> Last Modified
plt.cla()
plt.subplot(5, 1, 1)
plt.title("Days Before a Bug is Resolved")
ax1 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
ax1.set_ylim(2000, 3000)
ax1.spines['bottom'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)
ax1.set_facecolor("lightgrey")
ax1.set_ylabel("")
# plt.subplot(5, 1, 2)
# ax2 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
# ax2.set_ylim(200, 300)
# ax2.xaxis.set_visible(False)
# ax2.spines['bottom'].set_visible(False)
# ax2.spines['top'].set_visible(False)
# ax2.set_facecolor("lightgrey")
# ax2.set_ylabel("")
plt.subplot(5, 1, (2, 5))
ax3 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
ax3.set_ylim(0, 300)
ax3.spines['top'].set_visible(False)
ax3.xaxis.tick_bottom()
ax3.set_facecolor("lightgrey")
ax3.set_ylabel("")
plt.xlabel("Time Passed (Days)")
plt.ylabel("Count of Bugs")
plt.savefig("graphics/time_last_hist.pdf", bbox_inches='tight')
# plt.show()

# Scatter Plot Resolution vs. Modification for all bugs
plt.cla()
ax3 = res_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time")
ax3.set_xlabel("RESOLUTION TIME")
ax3.set_ylabel("MODIFICATION TIME")
plt.savefig("graphics/all_scatter.pdf", bbox_inches='tight')
# plt.show()

# Scatter Plot Resolution vs. Modification for WONTFIX bugs
plt.cla()
ax3 = wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time for WONTFIX bugs")
ax3.set_xlabel("RESOLUTION TIME")
ax3.set_ylabel("MODIFICATION TIME")
plt.savefig("graphics/wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()

# Scatter Plot Resolution vs. Modification w/o WONTFIX bugs
plt.cla()
ax3 = without_wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time for bugs NOT labeled WONTFIX")
ax3.set_xlabel("RESOLUTION TIME")
ax3.set_ylabel("MODIFICATION TIME")
plt.savefig("graphics/without_wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()

# Trend of resolved bugs created by year
plt.cla()
res_df["created_year"] = res_df.apply(lambda x: int(x['first_modified'][:4]), axis=1)
print("\nALL bugs resolution counts by year: \n", res_df.groupby('created_year')['bug_id'].count())
ax3 = res_df.groupby('created_year')['bug_id'].nunique().plot.line()

res_df["resolved_year"] = res_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
print("\nALL bugs resolution counts by year: \n", res_df.groupby('resolved_year')['bug_id'].count())
ax3 = res_df.groupby('resolved_year')['bug_id'].nunique().plot.line()

ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
# ax3.set_title("Trendline of Bug Resolutions Per Year")
ax3.set_xlabel("YEAR")
ax3.set_ylabel("COUNT OF BUGS")
ax3.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.f'))
plt.savefig("graphics/allbugs_trendlines.pdf", bbox_inches='tight')
# plt.show()

# Trend of WONTFIX bug resolutions by year
wontfix_df["resolved_year"] = wontfix_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
print("\nWONTFIX resolution counts by year: \n", wontfix_df.groupby('resolved_year')['bug_id'].count())
ax3 = wontfix_df.groupby('resolved_year')['bug_id'].nunique().plot.line()
ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
# ax3.set_title("Trendline of WONTFIX Bug Resolutions Per Year")
ax3.set_xlabel("YEAR")
plt.savefig("graphics/all_three_trendline.pdf", bbox_inches='tight')
# plt.show()

# Trend of WONTFIX bug resolutions by year
plt.cla()
wontfix_df["resolved_year"] = wontfix_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
print("\nWONTFIX resolution counts by year: \n", wontfix_df.groupby('resolved_year')['bug_id'].count())
ax3 = wontfix_df.groupby('resolved_year')['bug_id'].nunique().plot.line()
ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
# ax3.set_title("Trendline of WONTFIX Bug Resolutions Per Year")
ax3.set_xlabel("YEAR")
ax3.set_ylabel("COUNT OF BUGS")
ax3.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.f'))
plt.savefig("graphics/wontfix_trendline.pdf", bbox_inches='tight')
# plt.show()
