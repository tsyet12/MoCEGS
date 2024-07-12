from Pgraph.Pgraph import Pgraph #This is our Pgraph library
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv
import functools

import pandas as pd
import geopandas as gpd
import contextily as cx
from shapely.geometry import LineString
import os
import seaborn as sns
import numpy as np
import requests
import io
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
import pickle
import math
import copy
##### Helper functions for loading the CSV files #####
def to_float_with_default(strvalue, defvalue):
    try:
        value = float(strvalue)
        return 0 if pd.isna(value) else value
    except ValueError:
        return defvalue

def read_csv_to_array(filename):
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]

def read_column_from_csv_as_float(filename, column, key_column=0):
    try:
        data_df = pd.read_csv(filename, index_col=0)
        colname = data_df.columns[column-1]
        if key_column==0:
            return {index_value: to_float_with_default(data_df.loc[index_value,colname],0) for index_value in data_df.index}
        else:
            keyname = data_df.columns[key_column-1]
            return {data_df.loc[index_value,keyname]: to_float_with_default(data_df.loc[index_value,colname],0) for index_value in data_df.index}
    except:
        return {}

def df_data_to_float_with_interpolation(df, time_stamp, colname, default_value=0, allow_day_interpolation=True):
    ts_str = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    max_interpolate_timedelta = timedelta(days=1)
    if ts_str in df.index:
        return to_float_with_default(df.loc[ts_str,colname],default_value)
    else:
        if ts_str < df.index[0]:
            index_as_time = datetime.strptime(df.index[0], "%Y-%m-%d %H:%M:%S")
            if index_as_time - time_stamp < max_interpolate_timedelta:
                return to_float_with_default(df.loc[df.index[0],colname],default_value)
            else:
                return default_value
        elif ts_str > df.index[-1]:
            index_as_time = datetime.strptime(df.index[-1], "%Y-%m-%d %H:%M:%S")
            if time_stamp - index_as_time < max_interpolate_timedelta:
                return to_float_with_default(df.loc[df.index[-1],colname],default_value)
            else:
                return default_value
        else:
            # next_idx=1
            # while ts_str > df.index[next_idx]:
            #     next_idx = next_idx+1
            idx_low = 0
            idx_high = len(df.index)-1
            while idx_high-idx_low>1:
                next_idx = (idx_low+idx_high)//2
                if ts_str > df.index[next_idx]:
                    idx_low = next_idx
                else:
                    idx_high = next_idx
            next_idx = idx_high
            prev_time = datetime.strptime(df.index[next_idx-1], "%Y-%m-%d %H:%M:%S")
            next_time = datetime.strptime(df.index[next_idx], "%Y-%m-%d %H:%M:%S")
            prev_value = to_float_with_default(df.loc[df.index[next_idx-1],colname],default_value)
            next_value = to_float_with_default(df.loc[df.index[next_idx],colname],default_value)
            if next_time-prev_time < max_interpolate_timedelta:
                return prev_value+(next_value-prev_value)*((time_stamp-prev_time)/(next_time-prev_time))
            elif allow_day_interpolation:
                prev_day_value = df_data_to_float_with_interpolation(df, time_stamp-timedelta(days=1), colname, default_value, False)
                next_day_value = df_data_to_float_with_interpolation(df, time_stamp+timedelta(days=1), colname, default_value, False)
                return (prev_day_value+next_day_value)/2
        return default_value

def read_row_from_csv_as_float(filename, time_stamp):
    try:
        data_df = pd.read_csv(filename, index_col=0)
        return {colname: df_data_to_float_with_interpolation(data_df,time_stamp,colname) for colname in data_df.columns}
    except:
        return {}

def load_connectivity_data(filename):
    data_as_array = read_csv_to_array(filename)
    connectivity = {}
    for row_data in data_as_array:
        if row_data[0]=="":
            continue
        if row_data[1] in connectivity:
            connectivity[row_data[1]].add(row_data[2])
        else:
            connectivity[row_data[1]]=set([row_data[2]])
    return connectivity

def clip_value(value, minv, maxv):
    return min(maxv, max(minv, value))

def read_cell_from_csv_as_float(filename, time_stamp, col, default_value=0):
    try:
        data_df = pd.read_csv(filename, index_col=0)
        colname = data_df.columns[col-1]
        return df_data_to_float_with_interpolation(data_df,time_stamp,colname,default_value)
    except:
        return default_value

def capacity_comparator(item1, item2):
    if item1[0]<item2[0]:
        return -1
    elif item1[0]>item2[0]:
        return 1
    elif item1[1]<item2[1]:
        return -1
    elif item1[1]>item2[1]:
        return 1
    else:
        return 0
    
def find_largest_time_list(data_folder, station_list):
    time_list=[]
    for station in station_list:
        try:
            times_load=list(pd.read_csv(data_folder+"/load/"+station+".csv").iloc[:,0])
            if len(times_load) > len(time_list):
                time_list = times_load
        except:
            pass
        try:
            times_capacity=list(pd.read_csv(data_folder+"/capacity/"+station+".csv").iloc[:,0])
            if len(times_capacity) > len(time_list):
                time_list = times_capacity
        except:
            pass
        try:
            times_price=list(pd.read_csv(data_folder+"/price/"+station+"_"+station+".csv").iloc[:,0])
            if len(times_price) > len(time_list):
                time_list = times_price
        except:
            pass
    return time_list

##### Functions to fetch data #####
def zero_removal(number):
    if str(number)[0]=="0":
        return int(str(number)[1])
    else:
        return int(number)

def namespace_of_element(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''

def resolution_text_to_timedelta(resolution):
    if resolution=="PT15M":
        return timedelta(minutes=15)
    elif resolution=="PT30M":
        return timedelta(minutes=30)
    elif resolution=="PT60M":
        return timedelta(minutes=60)
    elif resolution=="PT1D":
        return timedelta(days=1)
    elif resolution=="PT1H":
        return timedelta(hours=1)
    elif resolution=="PT7D":
        return timedelta(days=7)
    elif resolution=="PT1Y":
        return timedelta(years=1)
    else:
        raise "Unknown time resolution"

def parse_time_series(time_series, namespace_name, unit_tag, value_tag):
    values = {}
    
    curve_type = time_series.find(namespace_name+"curveType").text
    period_data = time_series.find(namespace_name+"Period")
    interval_data = period_data.find(namespace_name+"timeInterval")
    interval_start = datetime.strptime(interval_data.find(namespace_name+"start").text, "%Y-%m-%dT%H:%MZ") #"%Y-%m-%dT%H:%M%z"
    interval_end = datetime.strptime(interval_data.find(namespace_name+"end").text, "%Y-%m-%dT%H:%MZ") #"%Y-%m-%dT%H:%M%z"
    resolution_text = period_data.find(namespace_name+"resolution").text
    resolution = resolution_text_to_timedelta(resolution_text)
    
    time_points = []
    for point_data in period_data.findall(namespace_name+'Point'):
        position = int(point_data.find(namespace_name+'position').text)
        quantity = float(point_data.find(namespace_name+value_tag).text)
        values[interval_start+resolution*(position-1)]=quantity
        time_points.append(interval_start+resolution*(position-1))
    if (curve_type=="A03"):
        time_points.sort()
        current_time = None
        for tp in time_points:
            if current_time != None:
                ct = current_time + resolution
                while ct < tp:
                    values[ct]=values[current_time]
                    ct = ct + resolution
            current_time = tp
        ct = current_time + resolution
        while ct < interval_end:
            values[ct]=values[current_time]
            ct = ct + resolution
    return {"business_type": time_series.find(namespace_name+"businessType").text, 
            "measure_unit": time_series.find(namespace_name+unit_tag).text,
            "resolution": resolution_text,
            "values": values}
    

def get_load(cin="10Y1001C--00137V",psrType="B19",start_time=datetime(2016,12,30,23,0,0),end_time=datetime(2016,12,31,23,0,0)):
    path=os.path.dirname(os.path.abspath(__file__))
    f = open(path+"\\token.txt", "r")
    token_str=f.read()
    
    start=start_time.strftime("%Y%m%d%H%M")
    end=end_time.strftime("%Y%m%d%H%M")

    param={
    "securityToken":token_str,
    "documentType": "A65",
    "ProcessType": "A16",
    #"psrType": "B09",
    "outBiddingZone_Domain": cin,
    "periodStart":start,
    "periodEnd":end} 


    response = requests.get('https://web-api.tp.entsoe.eu/api?', params=param)


    urlData=response.text
    try:
        root= ET.fromstring(urlData)
        #print(urlData)
        #print(response.content)
        
        # print(root.tag)
        # print(root.attrib)
        
        global_namespace = namespace_of_element(root)
        
        reason_tag = root.find(global_namespace+"Reason")
        if not (response.status_code==200 and response.reason=="OK"):
            if reason_tag is not None:
                reason_text = reason_tag.find(global_namespace+"text").text
                print(f"Request failed; response: {response.reason}, reason: {reason_text}")
            else:
                print(f"Request failed; response: {response.reason}")
            return None
        if reason_tag is not None:
            reason_text = reason_tag.find(global_namespace+"text").text
            print(f"Unable to get data, reason: {reason_text}")
            return None
        
        #df = pd.DataFrame([], columns=['Quantity', 'TimeSeries'], index=[])
        df = pd.DataFrame([], columns=['Quantity'], index=[])
        ts_index = 0
        for ts in root.findall(global_namespace+'TimeSeries'):
            ts_index = ts_index + 1
            ts_data = parse_time_series(ts, global_namespace, "quantity_Measure_Unit.name", "quantity")
            df.rename(columns = {'Quantity':'Quantity '+ts_data["measure_unit"]}, inplace = True)
            keys = list(ts_data["values"].keys())
            keys.sort()
            for time_stamp in keys:
               # df.loc[time_stamp]=[ts_data["values"][time_stamp], ts_index]
               df.loc[time_stamp]=[ts_data["values"][time_stamp]]
                
        #df['TimeSeries'] = df['TimeSeries'].astype('int')
        
        return df
        
    except Exception as e:
        print(e)
        #print(urlData)
    
    return None

def get_price(cin="10Y1001C--00137V", cout="10YSK-SEPS-----K",start_time=datetime(2016,12,30,23,0,0),end_time=datetime(2016,12,31,23,0,0)):
    path=os.path.dirname(os.path.abspath(__file__))
    f = open(path+"\\token.txt", "r")
    token_str=f.read()
    
    start=start_time.strftime("%Y%m%d%H%M")
    end=end_time.strftime("%Y%m%d%H%M")

    param={
    "securityToken":token_str,
    "DocumentType": "A44",
    "ProcessType": "A16",
    "in_Domain": cin,
    "out_Domain": cout,
    "periodStart":start,
    "periodEnd":end} 


    response = requests.get('https://web-api.tp.entsoe.eu/api?', params=param)

    urlData=response.text
    try:
        root= ET.fromstring(urlData)
        #print(urlData)
        #print(response.content)
        
        # print(root.tag)
        # print(root.attrib)
        
        global_namespace = namespace_of_element(root)
        
        reason_tag = root.find(global_namespace+"Reason")
        if not (response.status_code==200 and response.reason=="OK"):
            if reason_tag is not None:
                reason_text = reason_tag.find(global_namespace+"text").text
                print(f"Request failed; response: {response.reason}, reason: {reason_text}")
            else:
                print(f"Request failed; response: {response.reason}")
            return None
        if reason_tag is not None:
            reason_text = reason_tag.find(global_namespace+"text").text
            print(f"Unable to get data, reason: {reason_text}")
            return None
        
        #df = pd.DataFrame([], columns=['Quantity', 'TimeSeries'], index=[])
        df = pd.DataFrame([], columns=['Quantity'], index=[])
        ts_index = 0
        for ts in root.findall(global_namespace+'TimeSeries'):
            ts_index = ts_index + 1
            ts_data = parse_time_series(ts, global_namespace, "currency_Unit.name", "price.amount")
            df.rename(columns = {'Quantity':'Quantity '+ts_data["measure_unit"]}, inplace = True)
            keys = list(ts_data["values"].keys())
            keys.sort()
            for time_stamp in keys:
                #df.loc[time_stamp]=[ts_data["values"][time_stamp], ts_index]
                df.loc[time_stamp]=[ts_data["values"][time_stamp]]
                
        #df['TimeSeries'] = df['TimeSeries'].astype('int')
        
        return df
        
    except Exception as e:
        print(e)
        #print(urlData)
    
    return None

def get_generation(cin="10Y1001C--00137V",psrType="B19",start_time=datetime(2016,12,30,23,0,0),end_time=datetime(2016,12,31,23,0,0)):
    path=os.path.dirname(os.path.abspath(__file__))
    f = open(path+"\\token.txt", "r")
    token_str=f.read()

    start=start_time.strftime("%Y%m%d%H%M")
    end=end_time.strftime("%Y%m%d%H%M")
    
    param={
    "securityToken":token_str,
    "DocumentType": "A75",
    "ProcessType": "A16",
    #"BusinessType": "A01",
    #"psrType": "B09",
    "in_Domain": cin,
    "periodStart":start,
    "periodEnd":end} 


    response = requests.get('https://web-api.tp.entsoe.eu/api?', params=param)
    
    urlData=response.text
    try:
        root= ET.fromstring(urlData)
        #print(urlData)
        #print(response.content)
        
        # print(root.tag)
        # print(root.attrib)
        
        global_namespace = namespace_of_element(root)
        
        reason_tag = root.find(global_namespace+"Reason")
        if not (response.status_code==200 and response.reason=="OK"):
            if reason_tag is not None:
                reason_text = reason_tag.find(global_namespace+"text").text
                print(f"Request failed; response: {response.reason}, reason: {reason_text}")
            else:
                print(f"Request failed; response: {response.reason}")
            return None
        if reason_tag is not None:
            reason_text = reason_tag.find(global_namespace+"text").text
            print(f"Unable to get data, reason: {reason_text}")
            return None
        
        psr_list=[]
        psr_column_names=[]
        psr_index={}
        i=1
        for ts in root.findall(global_namespace+'TimeSeries'):
            psr_type = ts.find(global_namespace+"MktPSRType").find(global_namespace+"psrType").text
            if psr_type not in psr_list:
                psr_list.append(psr_type)
                psr_column_names.append('Quantity '+psr_type+' '+str(i))
                psr_index[psr_type]=i-1
                i=i+1
        
        # resolution_df = pd.DataFrame([], columns=['Resolution'], index=[])
        psr_df = {psr_type: pd.DataFrame([], columns=[psr_column_names[psr_index[psr_type]]], index=[]) for psr_type in psr_list}
        #ts_index = 0
        for ts in root.findall(global_namespace+'TimeSeries'):
            #ts_index = ts_index + 1
            psr_type = ts.find(global_namespace+"MktPSRType").find(global_namespace+"psrType").text
            if ts.find(global_namespace+"inBiddingZone_Domain.mRID") is not None: # or inBiddingZone???
                ts_data = parse_time_series(ts, global_namespace, "quantity_Measure_Unit.name", "quantity")
                keys = list(ts_data["values"].keys())
                keys.sort()
                for time_stamp in keys:
                    psr_df[psr_type].loc[time_stamp]=[ts_data["values"][time_stamp]]
                    # if time_stamp in resolution_df.index:
                    #     if resolution_df.loc[time_stamp]["Resolution"]!=ts_data["resolution"]:
                    #         raise "Inconsistent resolution"
                    # else:
                    #     resolution_df.loc[time_stamp]=[ts_data["resolution"]]
        
        df = pd.concat(list(psr_df.values()), axis=1)
        # df['TimeSeries'] = df['TimeSeries'].astype('int')
        
        return df
        
    except Exception as e:
        print(e)
        # print(urlData)
    
    return None

def get_physical_flows(cin="10Y1001C--00137V",cout="10YSK-SEPS-----K",start_time=datetime(2016,12,30,23,0,0),end_time=datetime(2016,12,31,23,0,0)):
    path=os.path.dirname(os.path.abspath(__file__))
    f = open(path+"\\token.txt", "r")
    token_str=f.read()
    
    start=start_time.strftime("%Y%m%d%H%M")
    end=end_time.strftime("%Y%m%d%H%M")

    param={
    "securityToken":token_str,
    "documentType": "A11",
    "in_Domain": cin,
    "out_Domain": cout,
    "periodStart":start,
    "periodEnd":end} 


    response = requests.get('https://web-api.tp.entsoe.eu/api?', params=param)


    urlData=response.text
    try:
        root= ET.fromstring(urlData)
        #print(urlData)
        #print(response.content)
        
        # print(root.tag)
        # print(root.attrib)
        
        global_namespace = namespace_of_element(root)
        
        reason_tag = root.find(global_namespace+"Reason")
        if not (response.status_code==200 and response.reason=="OK"):
            if reason_tag is not None:
                reason_text = reason_tag.find(global_namespace+"text").text
                print(f"Request failed; response: {response.reason}, reason: {reason_text}")
            else:
                print(f"Request failed; response: {response.reason}")
            return None
        if reason_tag is not None:
            reason_text = reason_tag.find(global_namespace+"text").text
            print(f"Unable to get data, reason: {reason_text}")
            return None
        
        #df = pd.DataFrame([], columns=['Quantity', 'TimeSeries'], index=[])
        df = pd.DataFrame([], columns=['Quantity'], index=[])
        ts_index = 0
        for ts in root.findall(global_namespace+'TimeSeries'):
            ts_index = ts_index + 1
            ts_data = parse_time_series(ts, global_namespace, "quantity_Measure_Unit.name", "quantity")
            df.rename(columns = {'Quantity':'Quantity '+ts_data["measure_unit"]}, inplace = True)
            keys = list(ts_data["values"].keys())
            keys.sort()
            for time_stamp in keys:
               # df.loc[time_stamp]=[ts_data["values"][time_stamp], ts_index]
               df.loc[time_stamp]=[ts_data["values"][time_stamp]]
                
        #df['TimeSeries'] = df['TimeSeries'].astype('int')
        
        return df
        
    except Exception as e:
        print(e)
        #print(urlData)
    
    return None

def fetch_all_data(start_time=datetime(2016,12,30,23,0,0),end_time=datetime(2016,12,31,23,0,0)):
    area=pd.read_csv(path+'\\areas.csv')
    code=list(area.iloc[:,0])
    # code=list(area.iloc[67:68,0])
    
    # start=start_time.strftime("%Y%m%d%H%M")
    # end=end_time.strftime("%Y%m%d%H%M")
    
    #log_list=[]
    
    print("\nLoad")
    for i in range(len(code)):
        print(f"Load for station: {code[i]}")
        flow=get_load(cin=code[i],start_time=start_time,end_time=end_time)
        if flow is not None:
            flow.to_csv(path+"//load//"+code[i]+".csv")
        #print(flow)
            
    print("\nCapacity")
    for i in range(len(code)):
        print(f"Capacity for station: {code[i]}")
        flow=get_generation(cin=code[i],start_time=start_time,end_time=end_time)
        if flow is not None:
            flow.to_csv(path+"//capacity//"+code[i]+".csv")
        #print(flow)
            
    print("\nPrice")
    for i in range(len(code)):
        print(f"Price for station: {code[i]}")
        flow=get_price(cin=code[i],cout=code[i],start_time=start_time,end_time=end_time)
        if flow is not None:
            flow.to_csv(path+"//price//"+code[i]+"_"+code[i]+".csv")
        #print(flow)
        
    print("\nPhysical flows")
    for i in range(len(code)):
        for k in range(len(code)):
            print(f"Physical flow from {code[i]} to {code[k]}")
            flow=get_physical_flows(cin=code[k],cout=code[i],start_time=start_time,end_time=end_time)
            if flow is not None:
                flow.to_csv(path+"//flow//"+code[i]+"_"+code[k]+".csv")
            #print(flow)

##### Function to remove file if it exists #####
def remove_file_if_possible(filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print(f"Error while deleting file {filename}: {e} ")

def remove_all_files_in_folder(folder_name):
    files = [f for f in os.listdir(folder_name) if os.path.isfile(folder_name+"\\"+f)]
    for file in files:
        remove_file_if_possible(folder_name+"\\"+file)

def clear_all_data():
    remove_all_files_in_folder(path+"\\load")
    remove_all_files_in_folder(path+"\\price")
    remove_all_files_in_folder(path+"\\capacity")
    remove_all_files_in_folder(path+"\\flow")

def clear_all_results():
    remove_all_files_in_folder(path+"\\P-graphs")
    remove_all_files_in_folder(path+"\\solutions")
    

path=os.path.dirname(os.path.abspath(__file__))

#%% Remove all previous figures
# clear_all_data()
# clear_all_results()

#%% Fetching data
start_time=datetime(2022, 1, 1, 0, 0, 0)
end_time=datetime(2023, 1, 1, 0, 0, 0)
# interval=timedelta(minutes=30)
#start_time=datetime(2022, 1,1, 0, 0, 0)
#end_time=datetime(2022, 1, 2, 0, 0, 0)
interval=timedelta(minutes=30)

#fetch_all_data(start_time=start_time,end_time=end_time)

#%% Solve and plot
total_connections=pd.DataFrame(columns=["unit","origin","destiny","value","normalized_value","time"])
    
# price_unit_correction_multiplier = 0.5 # units price is in MWh, but we only have 30 minute intervals
price_unit_correction_multiplier = interval / timedelta(hours=1)
environmental_impact_cost_factor = 1
transfer_cost_factor = 1
default_price_multiplier = 1000
#outside_eu_multiplier = 10

apply_border_penalty = True
use_margin_upper_bound = True
weigh_margin_with_population = True


area=pd.read_csv(path+'\\areas.csv')
stations=list(area.iloc[:,0])
connectivity_all = load_connectivity_data(path+"/connection.csv")
all_default_price = pd.read_csv(path+"/areas_updated_fix.csv", index_col=1)
all_station_capacity_raw = {station: pd.read_csv(path+"/capacity/"+station+".csv", index_col=0) for station in stations if os.path.isfile(path+"/capacity/"+station+".csv")}
all_price_raw = {station: pd.read_csv(path+"/price/"+station+"_"+station+".csv", index_col=0) for station in stations if os.path.isfile(path+"/price/"+station+"_"+station+".csv")}
all_station_demand = {station: pd.read_csv(path+"/load/"+station+".csv",index_col=0) for station in stations if os.path.isfile(path+"/load/"+station+".csv")}
environmental_impact = read_column_from_csv_as_float(path+"/env.csv", 1)
is_within_border = {station : True if all_default_price.loc[station,'EU'] == "YES" else False for station in stations}
# is_within_border = {station : True for station in stations}
is_margin_eu = {station : True if all_default_price.loc[station,'EU'] == "YES" else False for station in stations}

# Load real margin
if "total_margins_real" not in locals():
    total_margins_real = pd.read_pickle(path+"/total_margins_real.pkl")
  

other_currencies = ['BGN', 'UAH']
currency_history = {curr : pd.read_csv(path+"\\currencyRates\\"+curr+".csv", index_col=0) for curr in other_currencies}
for station,price_df in all_price_raw.items():
    if "Quantity EUR" not in price_df.columns:
        colname = price_df.columns[0]
        currname = colname.split()[1]
        price_df["Quantity EUR"] = [price_df.loc[idx,colname]*currency_history[currname].loc[idx.split()[0],"Rate"] if idx.split()[0] in currency_history[currname].index else all_default_price.loc[station,idx.split('-')[0]] for idx in price_df.index]


mapping = pd.read_csv(path+'\\areas_updated_fix.csv', header=0, index_col=0)
map_dict = {}

for i in range(mapping.shape[0]):
    map_dict.update({mapping.iloc[i, 0]: mapping.iloc[i, 2]})
    
dict_territories=pd.read_csv(path+"//dict_territories.csv",index_col=0)
territory_population = pd.read_csv(path+"//territory_population.csv", index_col=0)
min_population = min(territory_population["population"].values)
max_population = max(territory_population["population"].values)
population_divisor =2**math.floor(math.log(min_population,2)) #min_population #2**math.floor(math.log(min_population,2))/1000
station_territory = {}
for station in stations:
    map_code = map_dict[station]
    if map_code in dict_territories.index:
        station_territory[station] = dict_territories.loc[map_code]["territory"]
    elif station in total_margins_real['station'].values:
        print(f"station {station} has margin but no territory for {map_code}")


current_time = start_time
while current_time < end_time:
    
    print(f"\ncurrent time: {current_time}")
    #
    
    ##### Raw input data #####
    data_folder = path
    column_to_use = min(start_time.year-2011,11)  # 4 is 2015, 5 is 2016, ..., 11 is 2022
    #row_to_use = 12 # 0 is the header, 1 is the first data row
    
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    station_capacity_raw = {station: {colname: df_data_to_float_with_interpolation(all_station_capacity_raw[station],current_time,colname) for colname in all_station_capacity_raw[station].columns} if station in all_station_capacity_raw else {} for station in stations}
    default_price = {station : all_default_price.loc[station,str(start_time.year)]*default_price_multiplier for station in stations}
    price_raw = {station: df_data_to_float_with_interpolation(all_price_raw[station], current_time, "Quantity EUR", default_price[station]) if station in all_price_raw else default_price[station] for station in stations}
    station_demand = {station: df_data_to_float_with_interpolation(all_station_demand[station], current_time, "Quantity MAW", 0) if station in all_station_demand else 0 for station in stations}
    
    margin_df_current_time = total_margins_real[total_margins_real['time']==current_time_str]
    margin_upper_bound = {station: margin_df_current_time[margin_df_current_time['station']==map_dict[station]]['value'].iloc[0] if map_dict[station] in margin_df_current_time['station'].values else 0 for station in stations}

    ##### Algorithm input data transform #####
    station_capacity = {}
    for station, capacities in station_capacity_raw.items():
        capacity_list = [(source.split()[1],amount) for source, amount in capacities.items() if source != "Resolution"]
        capacity_list.sort(key=functools.cmp_to_key(capacity_comparator))
        final_capacities = {}
        for item in capacity_list:
            final_capacities[item[0]]=item[1]
        station_capacity[station]={source: value for source, value in final_capacities.items() if value>0}
            
    connectivity = {station: connections.intersection(stations) for station, connections in connectivity_all.items() if station in stations}
    price = {station: price*transfer_cost_factor*price_unit_correction_multiplier for station, price in price_raw.items()}
    margin_price = 2*max(price.values())
    
    ##### Generate the P-graph ######
    G = nx.DiGraph()
    material_count = 0
    unit_count = 0
    ME = []
    material_count = material_count+1
    demand_nodes = {}
    station_nodes = {}
    dict_short=dict()
    G.add_node("M"+str(material_count), names="Environmental Impact", type="raw_material", price=0.01*environmental_impact_cost_factor)
    material_count = material_count+1
    G.add_node("M"+str(material_count), names="Margin raw material", type="raw_material")
    transfer_unit_mapping = {}
    for station, demand in station_demand.items():
        if demand==0:
            continue
        material_count = material_count+1
        G.add_node("M"+str(material_count), names=station+" Demand", type="product", flow_rate_lower_bound=demand, flow_rate_upper_bound=demand)
        demand_nodes[station] = "M"+str(material_count)
    for station, capacities in station_capacity.items():
        material_count = material_count+1
        G.add_node("M"+str(material_count), names=station+" Total", type="intermediate")
        station_nodes[station]="M"+str(material_count)
        if station in demand_nodes:
            unit_count = unit_count+1
            G.add_node("O"+str(unit_count), names=station+" to "+station, proportional_cost=price[station])
            G.add_edge("M"+str(material_count), "O"+str(unit_count), weight=1)
            G.add_edge("O"+str(unit_count), demand_nodes[station], weight=1)
            
        if True: # add margin to every node
            unit_count = unit_count+1
            local_margin_price = margin_price
            if weigh_margin_with_population:
                if station in station_territory:
                    local_margin_price = margin_price * territory_population.loc[station_territory[station]]["population"] / population_divisor
                else:
                    local_margin_price = margin_price * max_population / population_divisor
            #if use_margin_upper_bound and is_margin_eu[station]:
            if use_margin_upper_bound:
                G.add_node("Om"+str(unit_count), names=station+" margin", proportional_cost=local_margin_price, capacity_upper_bound=margin_upper_bound[station])
            else:
                G.add_node("Om"+str(unit_count), names=station+" margin", proportional_cost=local_margin_price)
            G.add_edge("M2", "Om"+str(unit_count), weight=1)
            # G.add_edge("Om"+str(unit_count), demand_nodes[station], weight=1)
            G.add_edge("Om"+str(unit_count), station_nodes[station], weight=1)
            dict_short["Om"+str(unit_count)]=station
            
        for source, limit in capacities.items():
            if limit==0:
                continue
            material_count = material_count+1
            G.add_node("M"+str(material_count), names=station+" "+source+" Supply", type="raw_material", flow_rate_upper_bound=limit)
            unit_count = unit_count+1
            G.add_node("O"+str(unit_count), names=station+" "+source+" usage")
            G.add_edge("M"+str(material_count), "O"+str(unit_count), weight=1)
            G.add_edge("M1", "O"+str(unit_count), weight=environmental_impact[source])
            G.add_edge("O"+str(unit_count), station_nodes[station], weight=1)
    for station, connections in connectivity.items():
        for other_station in connections:
            if station<other_station: # to avoid adding the units twice
                acrossborder = is_within_border[station] != is_within_border[other_station]
                zero_connection_unit_count=0
                
                unit1 = "O"+str(unit_count+1)
                unit_count = unit_count+1
                if price[station]<=0:
                    zero_connection_unit_count = zero_connection_unit_count+1
                G.add_node(unit1, names=station+" to "+other_station, proportional_cost=(margin_price if (acrossborder and apply_border_penalty) else price[station]) if price[station]>0 else 0)
                G.add_edge(station_nodes[station], unit1, weight=1)
                G.add_edge(unit1, station_nodes[other_station], weight=1)
                transfer_unit_mapping[unit1]=(station, other_station)
                    
                unit2 = "O"+str(unit_count+1)
                unit_count = unit_count+1
                if price[other_station]<=0:
                    zero_connection_unit_count = zero_connection_unit_count+1
                G.add_node(unit2, names=other_station+" to "+station, proportional_cost=(margin_price if (acrossborder and apply_border_penalty) else price[other_station]) if price[other_station]>0 else 0)
                G.add_edge(station_nodes[other_station], unit2, weight=1)
                G.add_edge(unit2, station_nodes[station], weight=1)    
                transfer_unit_mapping[unit2]=(other_station, station)
                
                if zero_connection_unit_count==2:
                    ME.append([unit1,unit2])
    
    
    
    ##### Solve it #####
    P=Pgraph(problem_network=G, mutual_exclusion=ME, solver="INSIDEOUT",max_sol=1)
    P.run()
    #P.to_studio(path+"\\test_studio.pgsx")
    Solutions=P.goplist
    #if len(Solutions)==0:
    #    Solutions=Solutions1
    #    G=G1
    
    sol=Solutions[0] # Selection of solution to plot
    
    timename=current_time_str.replace(" ","_").replace(":","-")
    
    #G1=copy.copy(G) #Save previous timeslot
    #Solutions1=copy.copy(Solutions) #Save previous timeslot
    pickle.dump(G, open(path+"\\P-graphs\\"+timename+".txt", 'wb'))
    pickle.dump(sol, open(path+"\\solutions\\"+timename+".txt", 'wb'))
    
    current_time = current_time + interval
