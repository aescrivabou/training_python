#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 14:54:14 2024

@author: alvar
"""
#Load packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd

# Load data
county = pd.read_csv('County Impacts.csv')
city = pd.read_csv('City Impacts.csv')
state = pd.read_csv('State Impacts.csv')

#Merge data
impacts = county.merge(city, how='outer')
impacts = impacts.merge(state, how='outer')

#Convert dates into datetime
impacts['Post_Date'] = pd.to_datetime(impacts['Post_Date'], format='%m/%d/%Y')
impacts['Start_Date'] = pd.to_datetime(impacts['Start_Date'], format='%m/%d/%Y')
impacts['End_Date'] = pd.to_datetime(impacts['End_Date'], format='%m/%d/%Y')

#Unique impacts (dropping duplicative data)
unique_impacts = impacts.drop_duplicates("Id")


#Loop to create new dataframew with unique impacts by date
new_impacts = pd.DataFrame(columns=["Id", "date", "pos_imp"])

for i in range(len(unique_impacts)):
    current_day = unique_impacts.Start_Date.iloc[i]
    while current_day <= unique_impacts.End_Date.iloc[i]:
        new_row = pd.DataFrame([{"Id": unique_impacts.Id.iloc[i], "date" : current_day, "pos_imp":1}])
        new_impacts = pd.concat([new_impacts, new_row])
        current_day = current_day + pd.Timedelta(1, unit='D')
        print(i)


#All impacts by date
new_impacts = new_impacts.merge(unique_impacts, on="Id")

#Summary of daily impacts
new_impacts_day = new_impacts.groupby("date").sum().reset_index()


#Plot timelines
plt.plot(new_impacts_day.date, new_impacts_day.Total)
plt.plot(new_impacts_day.date, new_impacts_day.Agriculture)
plt.plot(new_impacts_day.date, new_impacts_day.Plants_And_Wildlife)

#Plot maps
county_shape = gpd.read_file('county_shape.shp').to_crs('epsg:3857')

county_sum = county.groupby("County").sum().reset_index()

county_shape_merged = county_shape.merge(county_sum, left_on= "FMNAME_PC", right_on='County')

county_shape_merged.plot(column="Plants_And_Wildlife" ,cmap = 'Reds', alpha = 0.7)

#Correlation
corr_data = unique_impacts[['Agriculture','Business_And_Industry', 'Energy', 'Fire', 'Plants_And_Wildlife','Relief_Response_And_Restrictions', 'Society_And_Public_Health', 'Tourism_And_Recreation', 'Water_Supply_And_Quality']]

corr = corr_data.corr()

fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(corr,cmap='coolwarm', vmin=-1, vmax=1)
fig.colorbar(cax)
ticks = np.arange(0,len(corr_data.columns),1)
ax.set_xticks(ticks)
plt.xticks(rotation=90)
ax.set_yticks(ticks)
ax.set_xticklabels(corr_data.columns)
ax.set_yticklabels(corr_data.columns)
plt.grid(color = 'white')
plt.show()


#Seaborn
import seaborn as sns
plt.figure(figsize=(16, 10))
mask = np.triu(np.ones_like(corr_data.corr(), dtype=bool))
heatmap = sns.heatmap(corr_data.corr(), mask=mask, vmin=-1, vmax=1, annot=True, cmap='PiYG')
heatmap.set_title('Triangle Correlation Heatmap', fontdict={'fontsize':18}, pad=16);
