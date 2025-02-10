import yaml

class GeneralUtils:
    """
    A utility class for general operations including reading YAML files and manipulating pandas DataFrames.
    Methods:
        get_yaml_values(file_path):
        compare_dfs(df_example, df_input):
        add_missing_cols(df_example, df_input):
        remove_additional_cols(df_example, df_input):

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

