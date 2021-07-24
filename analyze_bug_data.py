import pickle
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from brokenaxes import brokenaxes
import matplotlib.pyplot as plt
from pandas.core import nanops

# pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

infile = open("scraped_bug_data", 'rb')
bug_list = pickle.load(infile)
infile.close()


# make return time in days
def date_diff(date_one, date_two):
    # """returns the difference between two timestamps IN DAYS as a string"""
    t_d = (datetime.strptime(date_two[:10], '%Y-%m-%d').timestamp() -
           datetime.strptime(date_one[:10], '%Y-%m-%d').timestamp()) / 86400
    return t_d if t_d >= 0 else np.NaN


# def make_hyperlink(v):
#     url = "https://bugs.eclipse.org/bugs/show_bug.cgi?id={}"
#     return '=HYPERLINK("%s", "%s")' % (url.format(v), v)


# ------------------------------------------------- Create DF ----------------------------------------------------------

# df.append() creates a new df each time, use dicts instead then mass convert to DataFrame
bug_df = pd.DataFrame(bug_list)
bug_df = bug_df.replace({None: np.NaN})

bug_df['time_passed_touch'] = bug_df.apply(
    lambda x: date_diff(x['created'], x['first_modified']) if x['first_modified'] is not np.NaN else np.NaN, axis=1)

lst = ['RESOLVED', 'VERIFIED', 'CLOSED']

bug_df['time_passed_last'] = bug_df.apply(
    lambda x: date_diff(x['created'], x['last_modified']) if x['last_modified'] \
                                                             is not np.NaN and x['status'] in lst else np.NaN, axis=1)

# bug_df['bug_id'] = bug_df['bug_id'].apply(lambda x: make_hyperlink(x))

bug_df.to_excel("bug_data.xlsx")

# ------------------------------------------------- Analyze DF ---------------------------------------------------------

print("correlation:", bug_df["time_passed_touch"].corr(bug_df["time_passed_last"]))

res_df = bug_df[bug_df.status == 'RESOLVED'].append(
    bug_df[bug_df.status == 'CLOSED']).append(bug_df[bug_df.status == 'VERIFIED'])

touch_total = nanops.nansum(bug_df['time_passed_touch'])
res_total = nanops.nansum(res_df['time_passed_last'])
touch_count = bug_df['time_passed_touch'].count()
res_count = res_df['time_passed_last'].count()

print("touch_c: ", touch_count, " touch_t: ", touch_total, " avg: ", touch_total / touch_count)
print("res_c: ", res_count, " res_t: ", res_total, " avg: ", res_total / res_count)

touch_df = bug_df[bug_df.time_passed_touch.notnull()]
# print("\ntouch_df count: ", touch_df.count())

# ----- genie evaluation
genie_df = bug_df[bug_df.last_modified_author == 'genie'] \
    .append(bug_df[bug_df.last_modified_author == 'webmaster']) \
    # .append(bug_df[bug_df.last_modified_author == 'eclipse'])
# print("\ngenie resolved bugs: ", genie_df.count())

# print(genie_df.nlargest(10, 'time_passed_last'))

# print(genie_df[['time_passed_touch', 'time_passed_last']])
diff_series = genie_df['time_passed_last'] - genie_df['time_passed_touch']
# print(diff_series.nsmallest(3000))
# print(diff_series[diff_series == 0].count())
diff_sum = nanops.nansum(diff_series)
# print("dif: ", diff_sum, " avg: ", diff_sum/diff_series.count())

# print("\n\n", bug_df.groupby('last_modified_author')['bug_id'].count().nlargest(20))
# ----- genie eval end

# ----- WONTFIX eval
wontfix_df = bug_df[bug_df.resolution == 'WONTFIX']
# print("\n\n", wontfix_df.groupby('last_modified_author')['bug_id'].nunique().sort_values(ascending=False))
# print("\n", wontfix_df.count())
# print("\n\n", wontfix_df.groupby('last_modified_author')['bug_id'].count().nlargest(10))

# ----- WONTFIX eval end

without_wontfix_df = bug_df
cond = without_wontfix_df['bug_id'].isin(wontfix_df['bug_id'])
without_wontfix_df.drop(without_wontfix_df[cond].index, inplace=True)

# print(without_wontfix_df.nlargest(10, 'time_passed_last')).time

# ------------------------------------------------ Print Data ----------------------------------------------------------

# print("\n\n", bug_df.groupby('status')['bug_id'].nunique())
# print("\n\n", bug_df.groupby('resolution')['bug_id'].nunique())
# print("\n\n", bug_df.groupby(['status', 'resolution'])['bug_id'].nunique())

# print("touch: \n", bug_df.nlargest(15, 'time_passed_touch'))
# print("resolve: \n", bug_df.nlargest(15, 'time_passed_last'))

# -------------------- BrokenAxes Trial -------------------
# fig = plt.figure(figsize=(5, 2))
# bax = brokenaxes(ylims=((0, 35), (4000, 5000)), hspace=.05)
# x = np.linspace(0, 1, 100)
# bax.plot(touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60))
# bax.set_xlabel('Time Passed (Days)')
# bax.set_ylabel('Count of Bugs')
# ---------------------------------------------------------

# ----- Broken Axis touch Start ------------------------------------------------------------
# plt.subplot(4, 1, 1)
# ax1 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60)
# ax1.set_ylim(4000, 5000)
# ax1.spines['bottom'].set_visible(False)
# ax1.xaxis.tick_top()
# ax1.tick_params(labeltop=False)
# ax1.set_facecolor("lightgrey")
# ax1.set_ylabel("")
# plt.title("Days Before a Bug is Modified")
# plt.subplot(4, 1, (2, 4))
# ax3 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=60)
# ax3.set_ylim(0, 35)
# ax3.spines['top'].set_visible(False)
# ax3.xaxis.tick_bottom()
# ax3.set_facecolor("lightgrey")
# ax3.set_ylabel("")
# plt.xlabel("Time Passed (Days)")
# plt.ylabel("Count of Bugs")
# # plt.show()
# plt.savefig("graphs/time_touch_hist.pdf", bbox_inches='tight')
# plt.show()
# --------------------------------------------------------------- end

# ----- Broken Axis last Start ------------------------------------------------------------
# plt.subplot(5, 1, 1)
# plt.title("Days Before a Bug is Resolved")
# ax1 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
# ax1.set_ylim(2000, 3000)
# ax1.spines['bottom'].set_visible(False)
# ax1.xaxis.tick_top()
# ax1.tick_params(labeltop=False)
# ax1.set_facecolor("lightgrey")
# ax1.set_ylabel("")
# # plt.subplot(5, 1, 2)
# # ax2 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
# # ax2.set_ylim(200, 300)
# # ax2.xaxis.set_visible(False)
# # ax2.spines['bottom'].set_visible(False)
# # ax2.spines['top'].set_visible(False)
# # ax2.set_facecolor("lightgrey")
# # ax2.set_ylabel("")
# plt.subplot(5, 1, (2, 5))
# ax3 = touch_df['time_passed_last'].plot.hist(by='bug_id', bins=60)
# ax3.set_ylim(0, 300)
# ax3.spines['top'].set_visible(False)
# ax3.xaxis.tick_bottom()
# ax3.set_facecolor("lightgrey")
# ax3.set_ylabel("")
# plt.xlabel("Time Passed (Days)")
# plt.ylabel("Count of Bugs")
# plt.savefig("graphs/time_last_hist.pdf", bbox_inches='tight')
# plt.show()
# --------------------------------------------------------------- end

# ----- Scatter all Start --------------------------------------------------------------------
# ax3 = res_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
# ax3.set_ybound(-500, 7500)
# ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time")
# ax3.set_xlabel("RESOLUTION TIME")
# ax3.set_ylabel("MODIFICATION TIME")
# plt.savefig("graphs/all_scatter.pdf", bbox_inches='tight')
# plt.show()
# --------------------------------------------------------------- end

# ----- Scatter wontfix Start --------------------------------------------------------------------
# ax3 = wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
# ax3.set_ybound(-500, 7500)
# ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time for WONTFIX bugs")
# ax3.set_xlabel("RESOLUTION TIME")
# ax3.set_ylabel("MODIFICATION TIME")
# plt.savefig("graphs/wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()
# --------------------------------------------------------------- end

# ----- Scatter w/o wontfix Start --------------------------------------------------------------------
# ax3 = without_wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
# ax3.set_ybound(-500, 7500)
# ax3.set_xbound(-500, 7500)
# ax3.set_title("Resolution time vs. First Modified time for bugs NOT labeled WONTFIX")
# ax3.set_xlabel("RESOLUTION TIME")
# ax3.set_ylabel("MODIFICATION TIME")
# plt.savefig("graphs/without_wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()
# --------------------------------------------------------------- end

# ----- Scatter wontfix Start --------------------------------------------------------------------
wontfix_df["created_year"] = wontfix_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
print("counts: ", wontfix_df.groupby('created_year')['bug_id'].count())
ax3 = wontfix_df.groupby('created_year')['bug_id'].nunique().plot.line()
ax3.set_ybound(0, 750)
ax3.set_xbound(2000, 2020)
ax3.set_title("Resolution Year of bugs labeled WONTFIX")
ax3.set_xlabel("YEAR")
ax3.set_ylabel("COUNT OF BUGS")
plt.show()
# plt.savefig("graphs/wontfix_scatter.pdf", bbox_inches='tight')
# --------------------------------------------------------------- end

