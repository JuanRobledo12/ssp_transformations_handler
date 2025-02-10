import yaml

class GeneralUtils:
    """
    A utility class that provides general helper functions.
    Methods
    -------
    __init__():
        Initializes the GeneralUtils class.
    get_yaml_values(file_path):
        Reads a YAML file and retrieves specific values.
        Parameters:
        file_path (str): The path to the YAML file.
        Returns:
        dict: A dictionary containing the retrieved values.
        None: If the file is not found or there is an error parsing the YAML file.
    compare_dfs(df1, df2):
        Compares the columns of two DataFrames and prints the differences.
        Parameters:
        df1 (pandas.DataFrame): The first DataFrame.
        df2 (pandas.DataFrame): The second DataFrame.
    add_missing_cols(df1, df2):
        Adds missing columns from df1 to df2.
        Parameters:
        df1 (pandas.DataFrame): The first DataFrame.
        df2 (pandas.DataFrame): The second DataFrame.
        Returns:
        pandas.DataFrame: The second DataFrame with the missing columns added.
    """


    def __init__(self):
        """
        Initializes the instance of the class. Currently, this constructor does not perform any operations.
        """
        pass


    def get_yaml_values(sefl, file_path):
        """
        Reads a YAML file from the given file path and retrieves specific values.
        Args:
            file_path (str): The path to the YAML file.
        Returns:
            dict: A dictionary containing the retrieved values with keys:
                - "country_name" (str): The name of the country.
                - "ssp_input_file_name" (str): The name of the SSP input file.
                - "ssp_transformation_cw" (str): The SSP transformation CW value.
            None: If the file is not found or there is an error parsing the YAML file.
        Raises:
            FileNotFoundError: If the file is not found at the given file path.
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

    # Example usage
    if __name__ == "__main__":
        yaml_file_path = "path_to_your_file.yaml"  # Replace with the actual file path
        result = get_yaml_values(yaml_file_path)

        
    def compare_dfs(self, df_example, df_input):
        """
        Compares the columns of two pandas DataFrames and prints the differences.
        Parameters:
        df_example (pandas.DataFrame): The SSP example DataFrame to compare.
        df_input (pandas.DataFrame): Your input df DataFrame to compare.
        Returns:
        None
        Prints:
        - Columns present in df_example but not in df_input.
        - Columns present in df_input but not in df_example.
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

    def add_missing_cols(self, df_example, df_input):
        
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
    
    def remove_additional_cols(self, df_example, df_input):
        
        # Identify columns in df_input but not in df_example
        columns_to_remove = [col for col in df_input.columns if col not in df_example.columns]

        # Check if there are any columns to remove
        if not columns_to_remove:
            print("No additional columns to remove.")
            return df_input

        # Remove additional columns from df_input
        df_input = df_input.drop(columns=columns_to_remove)
        
        return df_input

