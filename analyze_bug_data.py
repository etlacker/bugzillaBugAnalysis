import pickle
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from brokenaxes import brokenaxes
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib import ticker
from pandas.core import nanops
# need to install openpyxl

save = True

pd.set_option("display.max_rows", None)
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
# The bug_data.xlsx that exists in this repository is the reviewed dataset.


# ------------------------------------------------- Analyze DF ---------------------------------------------------------

bug_df = pd.read_excel('bug_data.xlsx')
bug_df.drop(bug_df[bug_df['resolution'] == "NOT_ECLIPSE" ].index, inplace=True)

# print(bug_df.describe())

total_bugs = bug_df['bug_id'].count()
# print("Counts of Statuses in Full DB: \n", bug_df["status"].value_counts(dropna=False))
# print("\nCounts of Resolutions in Full DB: \n", bug_df["resolution"].value_counts(dropna=False))

print(bug_df['bug_id'].count())

res_df = bug_df[bug_df.status == 'RESOLVED'].append(
    bug_df[bug_df.status == 'CLOSED']).append(bug_df[bug_df.status == 'VERIFIED'])
print("\nCounts of Resolutions in Resolved DB: \n", res_df["resolution"].value_counts(dropna=False))
# print("\nMODE time_passed_last res_df: \n", res_df['time_passed_last'].value_counts())

fixed_df = res_df[res_df.resolution == 'FIXED']
fixed_total = nanops.nansum(fixed_df['time_passed_last'])
print("\nFixed count: ", fixed_df['bug_id'].count(), " fixed total: ", fixed_total,
      " avg: ", fixed_total/fixed_df['bug_id'].count())
# print("\nMODE time_passed_last fixed_df: \n", fixed_df['time_passed_last'].value_counts())
fixed_three_mo = fixed_df[fixed_df['time_passed_last'] < 93]
print("\nFIXED IN 3 MO: ", fixed_three_mo.count())

# nanops.nansum ignores null values, just like .count()
touch_total = nanops.nansum(bug_df['time_passed_touch'])
touch_count = bug_df['time_passed_touch'].count()

res_total = nanops.nansum(res_df['time_passed_last'])
res_count = res_df['time_passed_last'].count()

print("\ntouch_c: ", touch_count, " touch_t: ", touch_total, " avg: ", touch_total / touch_count)
print("res_c: ", res_count, " res_t: ", res_total, " avg: ", res_total / res_count)

touch_df = bug_df[bug_df.time_passed_touch.notnull()]
print("\ntouch_df count: \n", touch_df['bug_id'].count())

# Create subset with authors 'genie' and 'webmaster'
genie_df = bug_df[bug_df.last_modified_author == 'genie'] \
    .append(bug_df[bug_df.last_modified_author == 'webmaster'])
print("\ngenie/webmaster resolved bugs: ", genie_df['bug_id'].count())
# print("\ngenie_df largest time_passed_last: ", genie_df.nlargest(10, 'time_passed_last'))
# print("\nCounts of Resolutions in Genie DB: \n", genie_df["resolution"].value_counts(dropna=False))

# Create WONTFIX
wontfix_df = bug_df[bug_df.resolution == 'WONTFIX']
print("\nCounts of Authors in WONTFIX DB: \n", wontfix_df["last_modified_author"].value_counts(dropna=False))
close_origin_ct_wontfix = wontfix_df[(wontfix_df['time_passed_last'] <= 93)
                                     & (wontfix_df['time_passed_touch'] <= 93)]
print("\nwontfix origin ct: ", close_origin_ct_wontfix.count(), " total: ", wontfix_df.count())
print("\nWONTFIX avg closed time passed: ", wontfix_df['time_passed_last'].mean())

# Create subset w/o WONTFIX bugs
without_wontfix_df = res_df
cond = without_wontfix_df['bug_id'].isin(wontfix_df['bug_id'])
without_wontfix_df.drop(without_wontfix_df[cond].index, inplace=True)
close_origin_ct_wo_wontfix = without_wontfix_df[(without_wontfix_df['time_passed_last'] <= 93)
                                                & (without_wontfix_df['time_passed_touch'] <= 93)]
print("\nwo_wontfix origin ct: ", close_origin_ct_wo_wontfix.count(), " total: ", without_wontfix_df.count())
print("\nWO_WONTFIX avg closed time passed: ", without_wontfix_df['time_passed_last'].mean())

auto_closed_df = wontfix_df[wontfix_df.time_passed_last == wontfix_df.time_passed_touch]
print(auto_closed_df[auto_closed_df.time_passed_last == auto_closed_df.time_passed_last.max()])
print("\nautoclosed: \n", auto_closed_df.describe())

# Calculate and output rates
print("WONTFIX total: ", wontfix_df['bug_id'].count(), " WONTFIX rate: ",
      wontfix_df['bug_id'].count() / total_bugs)
print("RESOLVED total: ", res_df['bug_id'].count(), " RESOLVED rate: ",
      res_df['bug_id'].count() / total_bugs)
duplicate_count = bug_df[bug_df.resolution == 'DUPLICATE']
print("DUPLICATE total: ", duplicate_count['bug_id'].count(), " DUPLICATE rate: ",
      duplicate_count['bug_id'].count() / total_bugs)

# ---------------------------------------------- Print Graphics --------------------------------------------------------

# print("\n\n", bug_df.groupby('status')['bug_id'].nunique())
# print("\n\n", bug_df.groupby('resolution')['bug_id'].nunique())

# print("touch_largest: \n", bug_df.nlargest(15, 'time_passed_touch'))
# print("resolve_largest: \n", bug_df.nlargest(15, 'time_passed_last'))

# Broken Axis Histogram Submitted -> First Modified
plt.subplot(4, 1, 1)
ax1 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=51)
# print("\n value counts touch: \n", touch_df['time_passed_touch'].value_counts(bins=51))
# print("\n describe touch: \n", touch_df['time_passed_touch'].describe())
ax1.set_ylim(4000, 5000)
ax1.yaxis.tick_right()
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)
ax1.set_facecolor("lightgrey")
ax1.set_ylabel("")
plt.grid(axis='x')
plt.subplot(4, 1, (2, 4))
ax3 = touch_df['time_passed_touch'].plot.hist(by='bug_id', bins=51)
ax3.set_ylim(0, 40)
ax3.xaxis.tick_bottom()
ax3.set_facecolor("lightgrey")
ax3.set_ylabel("")
plt.xlabel("Time Passed (Days)", fontweight='bold')
plt.ylabel("Count of Bugs", fontweight='bold')
plt.grid(axis='x')
if save: plt.savefig("graphics/time_touch_hist.pdf", bbox_inches='tight')
# plt.show()

# Histogram First Modified -> First Bar
plt.cla()
plt.clf()
touch_lt_firstbar = touch_df[touch_df['time_passed_touch'] < 93]
# print("\ntt_df ct: ", touch_lt_firstbar.count())
ax1 = touch_lt_firstbar['time_passed_touch'].plot.hist(by='bug_id', bins=93)
ax1.set_facecolor("lightgrey")
plt.grid(axis='x')
plt.xlabel("Time Passed (Days)", fontweight='bold')
plt.ylabel("Count of Bugs", fontweight='bold')
if save: plt.savefig("graphics/time_touch_hist_firstbar.pdf", bbox_inches='tight')
# plt.show()

# Broken Axis Histogram Submitted -> Last Modified
plt.cla()
plt.clf()
plt.subplot(5, 1, 1)
ax1 = res_df['time_passed_last'].plot.hist(by='bug_id', bins=75)
# print("\n value counts res: \n", touch_df['time_passed_last'].value_counts(bins=75))
# print("\n describe last: \n", touch_df['time_passed_last'].describe())
ax1.set_ylim(2000, 3000)
ax1.yaxis.tick_right()
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)
ax1.set_facecolor("lightgrey")
ax1.set_ylabel("")
plt.grid(axis='x')
plt.subplot(5, 1, (2, 5))
ax3 = res_df['time_passed_last'].plot.hist(by='bug_id', bins=75)
ax3.set_ylim(0, 350)
ax3.xaxis.tick_bottom()
ax3.set_facecolor("lightgrey")
ax3.set_ylabel("")
plt.xlabel("Time Passed (Days)", fontweight='bold')
plt.ylabel("Count of Bugs", fontweight='bold')
plt.grid(axis='x')
if save: plt.savefig("graphics/time_last_hist.pdf", bbox_inches='tight')
# plt.show()

# Histogram Resolution Time -> First Bar
plt.cla()
plt.clf()
last_lt_firstbar = res_df[res_df['time_passed_last'] < 93]
# print("\nlt_df ct: ", last_lt_firstbar.count())
ax1 = last_lt_firstbar['time_passed_last'].plot.hist(by='bug_id', bins=93)
ax1.set_facecolor("lightgrey")
plt.grid(axis='x')
plt.xlabel("Time Passed (Days)", fontweight='bold')
plt.ylabel("Count of Bugs", fontweight='bold')
if save: plt.savefig("graphics/time_last_hist_firstbar.pdf", bbox_inches='tight')
# plt.show()

# Scatter Plot Resolution vs. Modification for all bugs
plt.cla()
plt.clf()
ax3 = res_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
ax3.set_xlabel("RESOLUTION TIME (days)", fontweight='bold')
ax3.set_ylabel("MODIFICATION TIME (days)", fontweight='bold')
if save: plt.savefig("graphics/all_scatter.pdf", bbox_inches='tight')
# plt.show()

# Scatter Plot Resolution vs. Modification for WONTFIX bugs
plt.cla()
plt.clf()
ax3 = wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
ax3.set_xlabel("RESOLUTION TIME (days)", fontweight='bold')
ax3.set_ylabel("MODIFICATION TIME (days)", fontweight='bold')
if save: plt.savefig("graphics/wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()

# Heatmap WONTFIX
plt.cla()
wontfix_heat = wontfix_df[wontfix_df[['time_passed_last', 'time_passed_touch']].notnull().all(axis=1)]
x = wontfix_heat['time_passed_last'].to_numpy()
y = wontfix_heat['time_passed_touch'].to_numpy()
heatmap, xedges, yedges = np.histogram2d(x, y, bins=50, density=True)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
plt.clf()
plt.imshow(heatmap.T, extent=extent, origin='lower', cmap=cm.Oranges, norm=LogNorm())
# plt.show()

# Scatter Plot Resolution vs. Modification w/o WONTFIX bugs
plt.cla()
plt.clf()
ax3 = without_wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3)
ax3.set_ybound(-500, 7500)
ax3.set_xbound(-500, 7500)
ax3.set_xlabel("RESOLUTION TIME (days)", fontweight='bold')
ax3.set_ylabel("MODIFICATION TIME (days)", fontweight='bold')
if save: plt.savefig("graphics/without_wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()

# Heatmap Without WONTFIX
plt.cla()
without_wontfix_heat = without_wontfix_df[without_wontfix_df[['time_passed_last', 'time_passed_touch']].notnull().all(axis=1)]
x = without_wontfix_heat['time_passed_last'].to_numpy()
y = without_wontfix_heat['time_passed_touch'].to_numpy()
heatmap, xedges, yedges = np.histogram2d(x, y, bins=50, density=True)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
plt.clf()
plt.imshow(heatmap.T, extent=extent, origin='lower', cmap=cm.Blues, norm=LogNorm())
# plt.show()

# Overlayed Scatter Plots
plt.cla()
plt.clf()
_, ax = plt.subplots()
wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3, c='red', ax=ax)
without_wontfix_df.plot.scatter(x="time_passed_last", y="time_passed_touch", s=3, ax=ax)
ax.set_ybound(-500, 7500)
ax.set_xbound(-500, 7500)
ax.set_xlabel("RESOLUTION TIME (days)", fontweight='bold')
ax.set_ylabel("MODIFICATION TIME (days)", fontweight='bold')
if save: plt.savefig("graphics/without_wontfix_scatter.pdf", bbox_inches='tight')
# plt.show()

# Trend of resolved bugs created by year
plt.cla()
plt.clf()
res_df["created_year"] = res_df.apply(lambda x: int(x['first_modified'][:4]), axis=1)
# print("\nALL bugs creation counts by year: \n", res_df.groupby('created_year')['bug_id'].count())
# print(res_df['created_year'].describe())
ax3 = res_df.groupby('created_year')['bug_id'].nunique().plot.line(style='-', color="#377eb8")

res_df["resolved_year"] = res_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
# print("\nALL bugs resolution counts by year: \n", res_df.groupby('resolved_year')['bug_id'].count())
# print(res_df['resolved_year'].describe())
ax3 = res_df.groupby('resolved_year')['bug_id'].nunique().plot.line(style=':', color="#e41a1c")

ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
ax3.set_xlabel("YEAR", fontweight='bold')
ax3.set_ylabel("COUNT OF BUGS", fontweight='bold')
ax3.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.f'))
plt.xticks(np.arange(2001, 2022, 3))
plt.legend(["Bug Submissions", "Closed Bugs"])
if save: plt.savefig("graphics/allbugs_trendlines.pdf", bbox_inches='tight')
# plt.show()

# Trend of WONTFIX bug resolutions by year (part of all 3)
wontfix_df["resolved_year"] = wontfix_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
# print("\nWONTFIX resolution counts by year: \n", wontfix_df.groupby('resolved_year')['bug_id'].count())
ax3 = wontfix_df.groupby('resolved_year')['bug_id'].nunique().plot.line(style='--', color="#4daf4a")
ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
ax3.set_xlabel("YEAR", fontweight='bold')
plt.xticks(np.arange(2001, 2022, 3))
plt.legend(["Bug Submissions", "Closed Bugs", "Closed WONTFIX Bugs"])
if save: plt.savefig("graphics/all_three_trendline.pdf", bbox_inches='tight')
# plt.show()

# Trend of WONTFIX bug resolutions by year
plt.cla()
wontfix_df["resolved_year"] = wontfix_df.apply(lambda x: int(x['last_modified'][:4]), axis=1)
print("\nWONTFIX resolution counts by year: \n", wontfix_df.groupby('resolved_year')['bug_id'].count())
ax3 = wontfix_df.groupby('resolved_year')['bug_id'].nunique().plot.line(style='--', color='#4daf4a')
ax3.set_ybound(0, 800)
ax3.set_xbound(2000, 2020)
ax3.set_xlabel("YEAR", fontweight='bold')
ax3.set_ylabel("COUNT OF BUGS", fontweight='bold')
ax3.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.f'))
plt.xticks(np.arange(2001, 2022, 3))
plt.legend(["Closed WONTFIX Bugs"])
if save: plt.savefig("graphics/wontfix_trendline.pdf", bbox_inches='tight')
# plt.show()
