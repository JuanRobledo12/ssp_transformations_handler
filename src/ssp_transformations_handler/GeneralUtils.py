import yaml
import pandas as pd
import os

class GeneralUtils:
    """
    A utility class for general operations including reading YAML files and manipulating pandas DataFrames.
    Methods:
        get_yaml_values(file_path):
        compare_dfs(df_example, df_input):
        add_missing_cols(df_example, df_input):
        remove_additional_cols(df_example, df_input):
        normalize_energy_frac_vars(df_to_norm, frac_vars_mapping_file_path):
    """
   
    @staticmethod
    def get_yaml_values(file_path):
        """
        Reads a YAML file and retrieves specific values.
        Args:
            file_path (str): The path to the YAML file.
        Returns:
            dict: A dictionary containing the retrieved values:
                - "country_name" (str): The name of the country.
                - "ssp_input_file_name" (str): The name of the SSP input file.
                - "ssp_transformation_cw" (str): The SSP transformation CW.
                - "energy_model_flag" (str): The energy model flag.
            None: If the file is not found or there is an error parsing the YAML file.
        Raises:
            FileNotFoundError: If the file is not found at the specified path.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        
        try:
            # Open and load the YAML file
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
            
            # Retrieve the specific values
            country_name = data.get("country_name", "Not found")
            ssp_input_file_name = data.get("ssp_input_file_name", "Not found")
            ssp_transformation_cw = data.get("ssp_transformation_cw", "Not found")
            energy_model_flag = data.get("energy_model_flag", "Not found")
            
            # Print the values
            print("Country Name:", country_name)
            print("SSP Input File Name:", ssp_input_file_name)
            print("SSP Transformation CW:", ssp_transformation_cw)
            print("Energy Model Flag:", energy_model_flag)
            
            # Return the values as a dictionary
            return {
                "country_name": country_name,
                "ssp_input_file_name": ssp_input_file_name,
                "ssp_transformation_cw": ssp_transformation_cw,
                "energy_model_flag": energy_model_flag
            }
        
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return None

    @staticmethod   
    def compare_dfs(df_example, df_input):
        """
        Compare the columns of two pandas DataFrames and print the differences.

        Parameters:
        df_example (pandas.DataFrame): The first DataFrame to compare.
        df_input (pandas.DataFrame): The second DataFrame to compare.

        Prints:
        Columns in df_example but not in df_input.
        Columns in df_input but not in df_example.
        """

        # Assuming your DataFrames are df_example and df_input
        columns_df_example = set(df_example.columns)
        columns_df_input = set(df_input.columns)

        # Columns present in df_example but not in df_input
        diff_in_df_example = columns_df_example - columns_df_input

        # Columns present in df_input but not in df_example
        diff_in_df_input = columns_df_input - columns_df_example

        print("Columns in df_example but not in df_input:", diff_in_df_example)
        print("Columns in df_input but not in df_example:", diff_in_df_input)

    @staticmethod
    def add_missing_cols(df_example, df_input):
        """
        Add missing columns from df_example to df_input.
        This function identifies columns that are present in df_example but 
        missing in df_input, and adds those columns to df_input with their 
        corresponding values from df_example.
        Parameters:
        df_example (pd.DataFrame): The DataFrame containing the example structure 
                                   with all required columns.
        df_input (pd.DataFrame): The DataFrame to which missing columns will be added.
        Returns:
        pd.DataFrame: The updated df_input DataFrame with missing columns added.
        """
        
        # Identify columns in df_example but not in df_input
        columns_to_add = [col for col in df_example.columns if col not in df_input.columns]

        # Check if there are any columns to add
        if not columns_to_add:
            print("No missing columns to add.")
            return df_input

        # Add missing columns to df2 with their values from df1
        for col in columns_to_add:
            df_input[col] = df_example[col]
        
        return df_input
    
    @staticmethod
    def remove_additional_cols(df_example, df_input):
        """
        Remove columns from df_input that are not present in df_example.
        Parameters:
        df_example (pandas.DataFrame): The reference DataFrame containing the desired columns.
        df_input (pandas.DataFrame): The DataFrame from which additional columns will be removed.
        Returns:
        pandas.DataFrame: A DataFrame with only the columns present in df_example.
        """
        
        # Identify columns in df_input but not in df_example
        columns_to_remove = [col for col in df_input.columns if col not in df_example.columns]

        # Check if there are any columns to remove
        if not columns_to_remove:
            print("No additional columns to remove.")
            return df_input

        # Remove additional columns from df_input
        df_input = df_input.drop(columns=columns_to_remove)
        
        return df_input
    

    @staticmethod
    def normalize_energy_frac_vars(df_to_norm, frac_vars_mapping_file_path):
        """
        Normalize energy fraction variables in a DataFrame.
        This function normalizes columns in the input DataFrame that correspond to energy fraction variables.
        The normalization is done by dividing each value in a subgroup of columns by the sum of the values in that subgroup for each row.
        The function also checks if the row sums for each subgroup are within the range [0, 1].
        Parameters:
        df_to_norm (pd.DataFrame): The DataFrame containing the data to be normalized.
        frac_vars_mapping_file_path (str): The file path to an Excel file that contains the mapping of energy fraction variables.
                                        The Excel file should have a column named 'prefix' which indicates the subgroup prefix for each variable.
        Returns:
        pd.DataFrame: A new DataFrame with the normalized energy fraction variables.
        """
       
        def test_sum(row_sums, subgroup_prefix):
            # get the sum of the row_sums
            row_sums_test = row_sums.sum() / len(row_sums)

            if row_sums_test < 0 or row_sums_test > 1:
                print(f"Row sums for {subgroup_prefix} are not in range, the sum is {row_sums_test}. Please check the data.")

            return None
            
        # Copy input df
        df = df_to_norm.copy()

        # Read energy frac vars
        df_frac_vars = pd.read_excel(frac_vars_mapping_file_path)
        
        # Get subgroup prefix list
        prefix_list = df_frac_vars['prefix'].unique()

        # Normalize subgroup cols
        for subgroup_prefix in prefix_list:
            # Get all columns belonging to the current subgroup
            subgroup_cols = [i for i in df.columns if subgroup_prefix in i]

            # Calculate the row-wise sum of the subgroup columns
            row_sums = df[subgroup_cols].sum(axis=1)

            # Check if the row sums are equal to 1
            test_sum(row_sums, subgroup_prefix)

            # Avoid division by zero; replace 0 sums with NaN
            row_sums = row_sums.replace(0, pd.NA)

            # Normalize each column in the subgroup by dividing by the row-wise sum
            df[subgroup_cols] = df[subgroup_cols].div(row_sums, axis=0)

        # Fill NaNs with 0
        df = df.fillna(0)

        return df
    
    @staticmethod
    def check_frac_groups(ssp_input_df, frac_vars_mapping_file_path):
        """
        Checks if the sum of fractional groups in the input DataFrame is within the range [0, 1].
        This function reads a mapping file to identify subgroups of columns in the input DataFrame.
        For each subgroup, it calculates the row-wise sum of the columns and checks if the sums are within the range [0, 1].
        If any row sum is outside this range, a message is printed indicating the issue.
        Args:
            ssp_input_df (pd.DataFrame): The input DataFrame containing the data to be checked.
            frac_vars_mapping_file_path (str): The file path to the Excel file containing the mapping of fractional variables.
        Returns:
            None
        """
        
       
        def test_sum(row_sums, subgroup_prefix):

            if row_sums.min() < 0 or row_sums.max() > 1:
                print(f"Row sums for {subgroup_prefix} are not in range the min is {row_sums.min()} and the max is {row_sums.max()}. Please check the data.")

            return None

        # Read energy frac vars
        df_frac_vars = pd.read_excel(frac_vars_mapping_file_path)
        
        # Get subgroup prefix list
        prefix_list = df_frac_vars['prefix'].unique()

        # Normalize subgroup cols
        for subgroup_prefix in prefix_list:
            # Get all columns belonging to the current subgroup
            subgroup_cols = [i for i in ssp_input_df.columns if subgroup_prefix in i]

            # Calculate the row-wise sum of the subgroup columns
            row_sums = ssp_input_df[subgroup_cols].sum(axis=1)

            # Check if the row sums are equal to 1
            test_sum(row_sums, subgroup_prefix)

        return None
    
    @staticmethod
    def check_individual_frac_vars(ssp_input_df):
        """
        Check if the values of individual fractional variables are within the range [0, 1].
        Parameters:
            ssp_input_df (pd.DataFrame): The DataFrame containing the SSP input data.
        Returns:
            None
        """
        #TODO: Implement this method

        # Get all columns that start with frac_
        frac_vars_cols = [col for col in ssp_input_df.columns if col.startswith('frac_')]

        # Check if the values are within the range [0, 1]
        for col in frac_vars_cols:
            if ssp_input_df[col].min() < 0 or ssp_input_df[col].max() > 1:
                print(f"Values in column {col} are not within the range [0, 1]. Please check the data.")
            else:
                pass
        
        return None

