#!/usr/bin/env python
# coding: utf-8
# author: Swarit Sankule

################################################
################ Anuj Pharma ###################
################################################

import numpy as np
import pandas as pd
import time
from datetime import datetime
from IPython.display import display, HTML
from IPython.core.interactiveshell import InteractiveShell
try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except:
    raise ValueError("Library not found | install on CMD using following command >>>>>  pip install fuzzywuzzy <<<<<<<<")
import os
import re
InteractiveShell.ast_node_interactivity = "all"
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
import warnings
warnings.filterwarnings('ignore')
print("Libraries Imported")
print(__name__)
# Define Class Object
class Class_DW():
    print("Creating Object...")

    def __init__(self):
        self.uname = 'swarit'
        self.server = 'tbd'
        self.db = 'tbd'
        self.pwd = 'tbd'

    # Main Function
    def python_script_func(self):

        ######################### Reading Files ################################
        path = os.getcwd()
        files = os.listdir(path + '\\input')

        try:
            # reading billing report
            r = re.compile("([Bb]ill)")
            file_name = list(filter(r.search, files))[0]
            print(f"Reading Billing Report ======>> {file_name}")
            billing_report_df = pd.read_excel(path + f'\\input\\{file_name}')

            # reading dispatch report
            r = re.compile("([Dd]is)")
            file_name = list(filter(r.search, files))[0]
            print(f"Reading Dispatch Report ======>> {file_name}")
            dispatch_report_df = pd.read_excel(path + f'\\input\\{file_name}')

            drug_mapping_df = pd.read_excel("input\drug_mapping.xlsx")
            hospital_mapping_df = pd.read_excel("input\hospital_mapping.xlsx")
        except:
            raise FileNotFoundError("Could not read files in 'input' directory | Check file names")

        print("-------------------------------------------")
        print("\n")
        # start time
        start = time.time()


        #########################################################################
        ######################### Billing Report ################################
        #########################################################################

        # extract actual column names
        real_column_names = billing_report_df.iloc[5,:]
        real_column_names = real_column_names.str.replace("\W","").str.lower().tolist()

        # index DF to the right number
        billing_report_df = billing_report_df.iloc[6:-1,]

        # renaming df
        billing_report_df.columns = real_column_names

        # reset index
        billing_report_df.reset_index(drop=True, inplace=True)

        #### Hospital Name

        # index of doc names
        doc_names_indices = billing_report_df.loc[billing_report_df['description'].isnull(),:].index.values.tolist()

        billing_report_df['hospital'] = '-'
        for i,count in enumerate(doc_names_indices):
        #     print(i, billing_report_df.iloc[count+1,0])
            if(count == max(doc_names_indices)):
                billing_report_df.iloc[count+1:,5] = billing_report_df.iloc[count+1,0]
            else:
                billing_report_df.iloc[count+1 : doc_names_indices[i+1],5] = billing_report_df.iloc[count+1,0]

        billing_report_df = billing_report_df.dropna()
        billing_report_df.reset_index(drop=True, inplace=True)

        #### Drug Name 

        # index of drug names
        drug_name_indices = billing_report_df.loc[~billing_report_df['description'].str.contains("[a-zA-Z]000"),:].index.values.tolist()

        # initiate drug name
        billing_report_df['drug'] = '-'

        # enumerate over drug list and impute values 
        for i,count in enumerate(drug_name_indices):
        #     print(i, billing_report_df.iloc[count,0])
            if(count == max(drug_name_indices)):
                billing_report_df.iloc[count:,6] = billing_report_df.iloc[count,0]
            else:
                billing_report_df.iloc[count : drug_name_indices[i+1],6] = billing_report_df.iloc[count,0]

        # cleaning rows with drug name
        billing_report_df = billing_report_df.loc[billing_report_df['description'].str.contains("[a-zA-Z]000"),:]
        billing_report_df.reset_index(drop=True, inplace=True)

        #### Splitting Description

        # concat to original axis = 1
        billing_report_df = pd.concat([billing_report_df,billing_report_df['description'].str.split(pat='\s+', n=2, expand=True)], axis=1)

        # renaming columns added
        billing_report_df.columns = ['description', 'qty', 'free', 'rate', 'amount', 'hospital', 'drug', 'order_id', 'date', 'batch_num']

        # remove description
        billing_report_df.drop(columns='description', inplace=True)

        # reset column poisitions as per heirarchy
        billing_report_df = billing_report_df.loc[:,['hospital', 'drug', 'order_id', 'date', 'batch_num', 'qty', 'free', 'rate', 'amount']]

        # replace junk with 0 and convert col to float
        billing_report_df[[ 'qty', 'rate', 'amount']] = billing_report_df[[ 'qty', 'rate', 'amount']].replace({"\W" : 0}, regex=True).astype(float)

        # proper casing
        billing_report_df['drug'] = billing_report_df['drug'].replace("\s+", " ", regex=True).str.strip().str.upper()

        # replacing null with hyphen
        billing_report_df['batch_num'].fillna("-", inplace=True)

        # save to excel
        billing_report_df.to_excel("output/billing_report_cleaned.xlsx", index=False)

        print("Cleaned Billing Report Saved!")



        ##########################################################################
        ######################### Dispatch Report ################################
        ##########################################################################

        # extract actual column names
        real_column_names = dispatch_report_df.iloc[5,:]
        real_column_names = real_column_names.str.replace("\W","").str.lower().tolist()

        # index DF to the right number
        dispatch_report_df = dispatch_report_df.iloc[6:-1,]

        # renaming df
        dispatch_report_df.columns = real_column_names

        # reset index
        dispatch_report_df.reset_index(drop=True, inplace=True)

        #### Hospital Name
        # index of doc names
        doc_names_indices = dispatch_report_df.loc[dispatch_report_df['description'].isnull(),:].index.values.tolist()

        dispatch_report_df['hospital'] = '-'
        for i,count in enumerate(doc_names_indices):
        #     print(i, dispatch_report_df.iloc[count+1,0])
            if(count == max(doc_names_indices)):
                dispatch_report_df.iloc[count+1:,5] = dispatch_report_df.iloc[count+1,0]
            else:
                dispatch_report_df.iloc[count+1 : doc_names_indices[i+1],5] = dispatch_report_df.iloc[count+1,0]

        dispatch_report_df = dispatch_report_df.dropna()
        dispatch_report_df.reset_index(drop=True, inplace=True)

        #### Drug Name 

        # index of drug names
        drug_name_indices = dispatch_report_df.loc[~dispatch_report_df['description'].str.contains("[a-zA-Z]000"),:].index.values.tolist()

        # initiate drug name
        dispatch_report_df['drug'] = '-'

        # enumerate over drug list and impute values 
        for i,count in enumerate(drug_name_indices):
        #     print(i, dispatch_report_df.iloc[count,0])
            if(count == max(drug_name_indices)):
                dispatch_report_df.iloc[count:,6] = dispatch_report_df.iloc[count,0]
            else:
                dispatch_report_df.iloc[count : drug_name_indices[i+1],6] = dispatch_report_df.iloc[count,0]

        # cleaning rows with drug name
        dispatch_report_df = dispatch_report_df.loc[dispatch_report_df['description'].str.contains("[a-zA-Z]000"),:]
        dispatch_report_df.reset_index(drop=True, inplace=True)

        #### Splitting Description

        # concat to original axis = 1
        dispatch_report_df = pd.concat([dispatch_report_df,dispatch_report_df['description'].str.split(pat='\s+', n=2, expand=True)], axis=1)

        # renaming columns added
        dispatch_report_df.columns = ['description', 'qty', 'free', 'rate', 'amount', 'hospital', 'drug', 'order_id', 'date', 'batch_num']

        # remove description
        dispatch_report_df.drop(columns='description', inplace=True)

        # reset column poisitions as per heirarchy
        dispatch_report_df = dispatch_report_df.loc[:,['hospital', 'drug', 'order_id', 'date', 'batch_num', 'qty', 'free', 'rate', 'amount']]

        # replace junk with 0 and convert col to float
        dispatch_report_df[[ 'qty', 'rate', 'amount']] = dispatch_report_df[[ 'qty', 'rate', 'amount']].replace({"\W" : 0}, regex=True).astype(float)

        # Clean and Format drug names for better string similarity
        dispatch_report_df['drug'] = dispatch_report_df['drug'].replace("\s+", " ", regex=True).str.strip().str.upper()

        # replace Null drug name with hyphen
        dispatch_report_df['batch_num'].fillna("-", inplace=True)

        #### Saving to Excel

        # save to excel
        dispatch_report_df.to_excel(r"output/dispatch_report_cleaned.xlsx", index=False)


        print("Cleaned Dispatch Report Saved!")
        print("-------------------------------------------")
        print("\n")



        #############################################################
        ########## Drug Name -- String Similarity   #################
        #############################################################


        # replace billing drug name with updated drug mapping (if any)
        drug_dict_to_replace = dict(zip(drug_mapping_df['billing_drug_name'], drug_mapping_df['dispatch_drug_name']))


        billing_drug_name_change = list(set(drug_mapping_df['billing_drug_name']) & set(billing_report_df['drug']))
        if(len(billing_drug_name_change) > 0):
            print("Mapping correct drug names....")
            # mapping correct names to billing data -- list of billing drug names to be changed
        #     billing_drug_name_change = drug_mapping_df['billing_drug_name'].tolist()
            # changing mismatched billing drug name to dispatch name
            billing_report_df.loc[billing_report_df['drug'].isin(billing_drug_name_change),'drug'] = billing_report_df.loc[billing_report_df['drug'].isin(billing_drug_name_change),'drug'].map(drug_dict_to_replace)
            print("Drug Mapping changed using 'drug_mapping' Excel | Proceeding ...")
        else:
            print("'drug_mapping' Excel empty!")


        # if(len(drug_dict_to_replace) > 0):
        #     print("Mapping correct drug names....")
        #     # mapping correct names to billing data -- list of billing drug names to be changed
        #     billing_drug_name_change = drug_mapping_df['billing_drug_name'].tolist()
        #     # changing mismatched billing drug name to dispatch name
        #     billing_report_df.loc[billing_report_df['drug'].isin(billing_drug_name_change),'drug'] = billing_report_df.loc[billing_report_df['drug'].isin(billing_drug_name_change),'drug'].map(drug_dict_to_replace)
        #     print("Drug Mapping changed using 'drug_mapping' Excel | Proceeding ...")
        # else:
        #     print("'drug_mapping' Excel empty!")

            
        # preparing dispatch drug DF
        dispatch_drug_df = pd.DataFrame(dispatch_report_df['drug'].unique())
        dispatch_drug_df.columns = ['dispatch_drug_name']

        # prepare billing drug DF
        billing_drug_df = pd.DataFrame(billing_report_df['drug'].unique())
        billing_drug_df.columns = ['billing_drug_name']

        # Defining function to get the right score and matches
        def match_name(namedf, names_list, min_score=0):
            # -1 score incase we don't get any matches
            max_score = -1
            # Returning empty name for no match as well
            max_name = ""
            # Iternating over all names in the correct list
            for name2 in names_list:
                #Finding fuzzy match score
                score = fuzz.ratio(namedf['dispatch_drug_name'], name2)
                # Checking if we are above our threshold and have a better score
                if (score > min_score) & (score > max_score):
                    max_name = name2
                    max_score = score
            return max_name, max_score

        # creating two columns
        dispatch_drug_df['similar_billing_drug_name'], dispatch_drug_df['match_prob'] = zip(*dispatch_drug_df.apply(lambda x: match_name(x, billing_drug_df['billing_drug_name'],0), axis=1))

        # define match_flag
        dispatch_drug_df['drug_match_flag'] = "No"
        dispatch_drug_df.loc[dispatch_drug_df['match_prob'] >= 60, 'drug_match_flag'] = "Yes"

        # Check for high probability mismatch cases
        mismatch_drugs = pd.DataFrame(dispatch_drug_df.loc[dispatch_drug_df['drug_match_flag'] != 'No','similar_billing_drug_name'].value_counts()).reset_index()
        mismatch_drugs = mismatch_drugs.loc[mismatch_drugs['similar_billing_drug_name'] > 1, 'index'].tolist()

        if(len(mismatch_drugs) >= 1):
            for drug in mismatch_drugs:
                max_prob = dispatch_drug_df.loc[dispatch_drug_df['similar_billing_drug_name'] == drug, 'match_prob'].max()
                dispatch_drug_df.loc[(dispatch_drug_df['similar_billing_drug_name'] == drug) & 
                                    (dispatch_drug_df['match_prob'] != max_prob), 'drug_match_flag'] = "No"

        # dispatch_drug_df.loc[dispatch_drug_df['drug_match_flag'] == 'No']
        extra_drugs_in_dispatch = dispatch_drug_df.loc[dispatch_drug_df['drug_match_flag'] == 'No', 'dispatch_drug_name']



        #########################################################
        ## Compare @ Hospital - Drug - Batch level mismatch
        ## **compare Billing and Dispath information** ##
        #########################################################

        dispatch_drug_df = dispatch_drug_df.loc[dispatch_drug_df['drug_match_flag'] == 'Yes']
        # save to excel
        dispatch_drug_df.to_excel(r"output\drug_match_list.xlsx", index=False)

        # if(dispatch_drug_df.shape[0] == dispatch_drug_df['similar_billing_drug_name'].nunique()):
        #     print("Drug mapping data ready!")
        # else:
        #     print("Mismatch in drug names | Rerun after checking any mismatch in drug names")

        # merge dispatch drug with billing report data
        billing_report_df_merged = billing_report_df.merge(dispatch_drug_df, 
                                how = 'left',
                                left_on='drug',
                                right_on='similar_billing_drug_name',validate="m:1")

        # drugs in billing report whose match is not found in dispatch report
        extra_drugs_in_billing = billing_report_df_merged.loc[billing_report_df_merged['dispatch_drug_name'].isna(), 'drug'].unique()

        if(len(extra_drugs_in_billing) > 0):
            print("Drugs in Billing Report not matched with Dispatch Report >>>")
            for drug in extra_drugs_in_billing:
                print(drug)
        else:
            print(" ********** All Drugs in Billing Report Matched! *************")

        # subset for selected columns
        billing_report_df_merged = billing_report_df_merged.loc[:,['hospital', 'batch_num', 'qty','drug','dispatch_drug_name']]

        # replace dispatch name with actual drug name if billing name is not found in drug mapping 
        billing_report_df_merged.loc[billing_report_df_merged['dispatch_drug_name'].isna(), 'dispatch_drug_name'] = billing_report_df_merged.loc[billing_report_df_merged['dispatch_drug_name'].isna(), 'drug']

        # save mismatch drug names to excel
        mismatch_list_dict = dict( {"billing_drug" : extra_drugs_in_billing,"dispatch_drug" : extra_drugs_in_dispatch})
        mismatch_list_df = pd.DataFrame.from_dict(mismatch_list_dict, orient='index')
        mismatch_list_df = mismatch_list_df.transpose()
        mismatch_list_df.fillna("", inplace=True)
        mismatch_list_df.to_excel(r'output\drug_mismatch_list.xlsx', index=False)

        print("-------------------------------------------")
        print("\n")



        ################################################################
        ###################### Comparison ##############################
        ################################################################

        billing_compare_df = billing_report_df_merged.groupby(['hospital', 'dispatch_drug_name', 'batch_num']).agg(billing_total_quantity = ('qty', 'sum')).reset_index()
        dispatch_compare_df = dispatch_report_df.groupby(['hospital', 'drug', 'batch_num']).agg(dispatch_total_quantity = ('qty', 'sum')).reset_index()

        # save mismatch drug names to excel
        mismatch_list_dict = dict( {"billing_drug" : extra_drugs_in_billing,"dispatch_drug" : extra_drugs_in_dispatch})
        mismatch_list_df = pd.DataFrame.from_dict(mismatch_list_dict, orient='index')
        mismatch_list_df = mismatch_list_df.transpose()
        mismatch_list_df.fillna("", inplace=True)
        mismatch_list_df.to_excel(r'output\drug_mismatch_list.xlsx', index=False)


        # replace billing hospital name with updated hospital (if any)
        dict_to_replace = dict(zip(hospital_mapping_df['billing_hospital_name'], hospital_mapping_df['dispatch_hospital_name']))

        billing_hospital_name_change = list(set(hospital_mapping_df['billing_hospital_name']) & set(billing_compare_df['hospital']))

        if(len(billing_hospital_name_change) > 0):
                # mapping correct names to billing data -- list of billing hospital names to be changed
        #         billing_hospital_name_change = list(set(billing_compare_df['hospital']) - set(dispatch_compare_df['hospital']))
                billing_compare_df.loc[billing_compare_df['hospital'].isin(billing_hospital_name_change),'hospital'] = billing_compare_df.loc[billing_compare_df['hospital'].isin(billing_hospital_name_change),'hospital'].map(dict_to_replace)
                print("Hospital Mapping changed using 'hospital_mapping' Excel | Proceeding ...")
        else:
            print("'hospital_mapping' Excel empty!")

        # list of hospitals in billing not found in dispatch
        if(len(set(billing_compare_df['hospital']) - set(dispatch_compare_df['hospital']))>0):
            print("List of billing hospital names not matching in dispatch data >>> ")
            for hosp in (set(billing_compare_df['hospital']) - set(dispatch_compare_df['hospital'])):
                print(hosp)
            print("\n")

        # save mismatch hospital names to excel
        mismatch_hosp_dict = dict({"billing_hospital_name" : (set(billing_compare_df['hospital']) - set(dispatch_compare_df['hospital'])),"dispatch_hospital_name" : (set(dispatch_compare_df['hospital']) - set(billing_compare_df['hospital']))})
        mismatch_hosp_df = pd.DataFrame.from_dict(mismatch_hosp_dict, orient='index')
        mismatch_hosp_df = mismatch_hosp_df.transpose()
        mismatch_hosp_df = mismatch_hosp_df.fillna("")
        mismatch_hosp_df.to_excel(r'output\hospital_mismatch_list.xlsx', index=False)
            
        print("-------------------------------------------")
        print(f"Number of Hospital in Billing ==> {billing_compare_df['hospital'].nunique()}")
        print(f"Number of Hospital in Dispatch ==> {billing_compare_df['hospital'].nunique()}")
        print(f"Number of Hospital Matching ==> {len(set(billing_compare_df['hospital']) & set(dispatch_compare_df['hospital']))}")
        print("-------------------------------------------")

        if(len(set(billing_compare_df['hospital']) & set(dispatch_compare_df['hospital'])) == 0):
            raise ValueError("No Hospital Matching -- Check Data Manually")
                    
        if(len(set(billing_compare_df['hospital']) - set(dispatch_compare_df['hospital']))==0):
            print("************ Hospital names matched! ***************")
            
        # column name change for simple merging
        billing_compare_df.rename(columns={'dispatch_drug_name' : 'drug'}, inplace=True)

            
        # creating comparsion DF
        try:
            final_comparison_df = billing_compare_df.merge(dispatch_compare_df,
                                                                    how = 'outer',
                                                                    on=['hospital', 'drug', 'batch_num'],
                                                                    validate="1:1")
        except:
            raise ValueError("ONE to ONE mapping not present | multiple [Hospital - Drug - Batch] combintation present")

        # missing values as 0
        final_comparison_df.loc[:,['billing_total_quantity', 'dispatch_total_quantity']] = final_comparison_df.loc[:,['billing_total_quantity', 'dispatch_total_quantity']].fillna(0)

        # remaining quantity to dispatch
        final_comparison_df['to_dispatch'] = final_comparison_df['billing_total_quantity'] - final_comparison_df['dispatch_total_quantity']
                    
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(r'output\billing_and_dispatch_comparison.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        final_comparison_df.to_excel(writer, sheet_name='to_dispatch', index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets['to_dispatch']

        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                                    'font_color': '#9C0006'})

        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                                    'font_color': '#006100'})

        # Apply a conditional format to the cell range.
        worksheet.conditional_format('F2:F99999', {'type':     'cell',
                                                'criteria': '<',
                                                'value':    0,
                                                'format':   format1})

        # Write another conditional format over the same range.
        worksheet.conditional_format('F2:F99999', {'type': 'cell',
                                                'criteria': '>',
                                                'value': 0,
                                                'format': format2})

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()


        # done!
        print("\n")
        print("Process complete!  |  Validate Outputs")
        end = time.time()
        hours, rem = divmod(end-start, 3600)
        minutes, seconds = divmod(rem, 60)
        print("Execution Time ==> {:0>2}:{:05.2f}".format(int(minutes),seconds))
        return 0


if (__name__ == "__main__"):
    py_obj = Class_DW()
    py_obj.python_script_func()