import os
import pandas as pd
import yaml


class TransformationYamlProcessor:
    """
    TransformationYamlProcessor is a class designed to handle the processing of YAML files based on scenario mappings provided in an Excel file. It provides methods to load scenario mappings, retrieve strategy names, load YAML data, save modified YAML files, and process YAML files according to specified transformations.
    Methods:
        __init__(self, scenario_mapping_excel_path, yaml_dir_path, sheet_name='yaml'):
            Initializes the TransformationYamlProcessor class with the given parameters.
        load_scenario_mapping_excel(self):
        load_yaml_data(self, yaml_file_path):
        get_strategy_names(self):
        save_yaml_file(self, yaml_content, yaml_name, column, transformation_code, subsector, transformation_name, scalar_val):
        get_transformations_per_strategy_dict(self):
        process_yaml_files(self):
    """
    
    def __init__(self, scenario_mapping_excel_path, yaml_dir_path, main_sheet_name='main', yaml_sheet_name='yaml'):
        """
        Initializes the TransformationUtils class with paths and sheet names for scenario mapping and YAML files.
        Args:
            scenario_mapping_excel_path (str): Path to the Excel file containing scenario mappings.
            yaml_dir_path (str): Directory path where YAML files are stored.
            main_sheet_name (str, optional): Name of the main sheet in the Excel file. Defaults to 'main'.
            yaml_sheet_name (str, optional): Name of the YAML sheet in the Excel file. Defaults to 'yaml'.
        Attributes:
            scenario_mapping_excel_path (str): Stores the path to the scenario mapping Excel file.
            main_sheet_name (str): Stores the name of the main sheet.
            yaml_sheet_name (str): Stores the name of the YAML sheet.
            yaml_dir_path (str): Stores the directory path for YAML files.
            mapping_df (pd.DataFrame): DataFrame containing the loaded scenario mapping from Excel.
        """
        self.scenario_mapping_excel_path = scenario_mapping_excel_path
        self.main_sheet_name = main_sheet_name
        self.yaml_sheet_name = yaml_sheet_name
        self.yaml_dir_path = yaml_dir_path
        self.mapping_df = self.load_scenario_mapping_excel(excel_path=self.scenario_mapping_excel_path)
        self._configure_yaml_representer()

    class CustomDumper(yaml.SafeDumper):
        def represent_str(self, data):
            # Use explicit double quote style for strings that require quoting.
            if isinstance(data, str) and (':' in data or '"' in data):
                return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')
            return self.represent_scalar('tag:yaml.org,2002:str', data)
    
    def _configure_yaml_representer(self):
        # Register the custom representer for strings with our CustomDumper.
        yaml.add_representer(str, self.CustomDumper.represent_str, Dumper=self.CustomDumper)

    def load_scenario_mapping_excel(
        self,
        excel_path: str,
        transformation_code_col: str = "transformation_code",
        start_period_col: str = "start_period",
        strategy_prefix: str = "strategy"
    ) -> pd.DataFrame:
        """
        Loads the 'main' and 'yaml' sheets from an Excel file, filters the main sheet for the
        transformation_code, start_period, and strategy columns, then merges with the yaml sheet
        on transformation_code.

        Args:
            excel_path (str): Path to the Excel file.
            transformation_code_col (str): Name of the transformation code column. Default is 'transformation_code'.
            start_period_col (str): Name of the start period column. Default is 'start_period'.
            strategy_prefix (str): Prefix for strategy columns. Default is 'strategy'.

        Returns:
            pd.DataFrame: The merged DataFrame, or None if an error occurs.
        """
        try:
            df_main = pd.read_excel(excel_path, sheet_name=self.main_sheet_name)
        except Exception as e:
            print(f"Error loading main sheet '{self.main_sheet_name}' from {excel_path}: {e}")
            return None

        try:
            cols_to_keep = [transformation_code_col, start_period_col] + \
                        [col for col in df_main.columns if col.startswith(strategy_prefix)]
            missing_cols = [col for col in [transformation_code_col, start_period_col] if col not in df_main.columns]
            if missing_cols:
                print(f"Missing columns in main sheet: {missing_cols}")
                return None
            df_main_filtered = df_main[cols_to_keep]
        except Exception as e:
            print(f"Error filtering columns in main sheet: {e}")
            return None

        try:
            df_yaml = pd.read_excel(excel_path, sheet_name=self.yaml_sheet_name)
        except Exception as e:
            print(f"Error loading yaml sheet '{self.yaml_sheet_name}' from {excel_path}: {e}")
            return None

        if transformation_code_col not in df_yaml.columns:
            print(f"Column '{transformation_code_col}' not found in yaml sheet.")
            return None

        try:
            df_merged = pd.merge(df_yaml, df_main_filtered, on=transformation_code_col, how="left")
        except Exception as e:
            print(f"Error merging dataframes: {e}")
            return None

        return df_merged

    
    def load_yaml_data(self, yaml_file_path):
        """
        Load the content of a YAML file into a dictionary.
        This method reads the content of a YAML file specified by the `yaml_file` 
        parameter and returns the data as a dictionary.
        Args:
            yaml_file (str): The path to the YAML file to load.
        Returns:
            dict: A dictionary containing the data from the YAML file.
        """
        with open(yaml_file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        return yaml_data
    
    
    def get_strategy_names(self):
        """
        Retrieve column names that start with 'strategy'.
        This method filters the columns of the DataFrame stored in the `data` attribute
        and returns a list of column names that begin with the prefix 'strategy'.
        Returns:
            list: A list of column names that start with 'strategy'.
        """
        # Get col names
        col_names = self.mapping_df.columns
       
        # return only strategy col names
        return [col for col in col_names if col.startswith('strategy')]
    
    def save_yaml_file(self, yaml_content, yaml_name, column, transformation_code, subsector, transformation_name, scalar_val):
        """
        Save the given YAML content to a file with a modified name and updated identifiers.
        Args:
            yaml_content (dict): The content to be saved in the YAML file.
            yaml_name (str): The original name of the YAML file.
            column (str): The column name to be included in the transformation code and new file name.
            transformation_code (str): The transformation code to be updated.
            subsector (str): The subsector to be used in the transformation name.
            transformation_name (str): The transformation name to be updated.
            scalar_val (float): The scalar value applied to the parameters.
        """
        # Update identifiers with the proper naming
        yaml_content['identifiers']['transformation_code'] = f"{transformation_code}_{column.upper()}"
        yaml_content['identifiers']['transformation_name'] = f"Scaled Default Max Parameters by {scalar_val} - {subsector}: {transformation_name}"
        
        # Update description and transformer if needed (currently just resetting them)
        description = yaml_content['description']
        transformer = yaml_content['transformer']
        yaml_content['description'] = f"{description}"
        yaml_content['transformer'] = f"{transformer}"

        new_yaml_name = f"{os.path.splitext(yaml_name)[0]}_{column}.yaml"
        new_yaml_path = os.path.join(self.yaml_dir_path, new_yaml_name)
        with open(new_yaml_path, 'w') as new_file:
            yaml.dump(yaml_content, new_file, Dumper=self.CustomDumper, default_flow_style=False)
        
    
    def get_transformations_per_strategy_dict(self):
        """
        Generates a dictionary of transformation codes for each strategy.

        This method retrieves strategy names and loads data from an Excel file.
        For each strategy, it creates a subset of the data containing transformation
        codes and the strategy column, removes rows with missing values, and formats
        the transformation codes by appending the strategy name in uppercase.
        The result is a dictionary where each key is a strategy name and the value
        is a list of formatted transformation codes.

        Returns:
            dict: A dictionary where keys are strategy names and values are lists
                  of formatted transformation codes.
        """

        transformations_per_strategy = {}
        strategy_names =  self.get_strategy_names()
        df = self.mapping_df.copy()
        for strategy in strategy_names:
            subset_df = df[['transformation_code', strategy]]
            subset_df = subset_df.dropna()
            subset_transformation_codes = subset_df['transformation_code'].tolist()
            subset_transformation_codes = [f"{code}_{strategy.upper()}" for code in subset_transformation_codes]
            transformations_per_strategy[strategy] = subset_transformation_codes
        return transformations_per_strategy

    def overwrite_yaml_to_default(self, yaml_file_path):
        #TODO: Implement this method
        pass
    
    
    
    def process_yaml_files(self):
        """
        Processes YAML files based on the mapping DataFrame and updates them according to strategy-specific scalar values.

        This method iterates over each row in the mapping DataFrame (`self.mapping_df`), which should contain information about
        transformation YAML files, transformation codes, names, subsectors, start periods, and strategy columns with scalar values.
        For each strategy with a non-null scalar value, it loads the corresponding YAML file, updates its parameters (such as
        'magnitude' and 'vec_implementation_ramp'), and saves the modified YAML file with a strategy-specific name.

        Raises:
            ValueError: If the mapping DataFrame is None or empty.

        Workflow:
            - For each row in the mapping DataFrame:
                - Checks if the corresponding YAML file exists.
                - For each strategy column:
                    - If a scalar value is present, loads the YAML file.
                    - Updates the 'magnitude' parameter by multiplying it with the scalar value, if present.
                    - Ensures 'vec_implementation_ramp' and 'tp_0_ramp' are set in parameters.
                    - Saves the updated YAML file with a new name reflecting the strategy.
                    - Handles special cases where 'magnitude' is missing.
                - Handles and logs errors during processing.

        Notes:
            - Expects helper methods: `get_strategy_names()`, `load_yaml_data()`, and `save_yaml_file()`.
            - Prints status messages and warnings for missing files or attributes.
            - Does not overwrite existing strategy-specific YAML files unless 'magnitude' is present.
        """
        # Check if mapping df is none or empty
        if self.mapping_df is None or self.mapping_df.empty:
            raise ValueError("No data found in the mapping excel file.")

        # Loop over each row in the Scenario Mapping Excel
        for _, row in self.mapping_df.iterrows():
            yaml_name = row['transformation_yaml_name']
            transformation_code = row['transformation_code']
            transformation_name = row['transformation_name']
            subsector = row['subsector']
            start_period = row['start_period']
            yaml_path = os.path.join(self.yaml_dir_path, yaml_name)

            if not os.path.exists(yaml_path):
                print(f"Original YAML file {yaml_name} not found in directory {self.yaml_dir_path}.")
                continue

            for column in self.get_strategy_names():
                scalar_val = row[column]
                if pd.isna(scalar_val):
                    continue

                print("="*50)
                print(f"[{yaml_name} | {transformation_code}] {transformation_name} ({subsector}) | Start: {start_period}")
                print(f"Strategy: {column}, Scalar value: {scalar_val}")

                try:
                    yaml_content = self.load_yaml_data(yaml_path)
                    parameters = yaml_content.get('parameters')
                    if not parameters:
                        print(f"YAML file {yaml_name} for strategy {column} missing 'parameters' attribute. Please check manually.")
                        continue

                    # Helper: always update or create vec_implementation_ramp dict and tp_0_ramp
                    def set_vec_implementation_ramp(params, start_period):
                        if not isinstance(params.get('vec_implementation_ramp'), dict):
                            params['vec_implementation_ramp'] = {}
                        params['vec_implementation_ramp']['tp_0_ramp'] = int(start_period)

                    # Main logic for "magnitude" attribute
                    if 'magnitude' in parameters:
                        curr_magnitude = float(parameters['magnitude'])
                        parameters['magnitude'] = float(scalar_val) * curr_magnitude
                        set_vec_implementation_ramp(parameters, start_period)
                        self.save_yaml_file(yaml_content, yaml_name, column, transformation_code, subsector, transformation_name, scalar_val)

                    # Special case: no magnitude
                    else:
                        yaml_out_path = os.path.join(self.yaml_dir_path, f"{os.path.splitext(yaml_name)[0]}_{column}.yaml")
                        if os.path.exists(yaml_out_path):
                            print(f"YAML file {yaml_name} already exists for strategy {column}. Please check manually.")
                            continue
                        print(f"Created new YAML file {yaml_name} for strategy {column} (special case, no magnitude)")
                        set_vec_implementation_ramp(parameters, start_period)
                        self.save_yaml_file(yaml_content, yaml_name, column, transformation_code, subsector, transformation_name, scalar_val)

                except Exception as e:
                    print(f"Error processing file {yaml_name} for column {column}: {e}")

                print("="*50)

class StrategyCSVHandler:
    """
    A class to handle strategy CSV files and YAML mappings for transformations.
    Methods:
        __init__(csv_file_path, yaml_dir_path, yaml_mapping_file, transformation_per_strategy_dict):
            Initializes the StrategyCSVHandler class with the given parameters.
        load_strategy_definitions_csv():
        load_yaml_mapping():
        get_strategy_id(strategy_group):
        get_strategy_code(strategy_group, strategy_name):
        get_transformation_specification(yaml_file_suffix):
        save_csv():
        add_strategy(strategy_group, description, yaml_file_suffix):
    """

    def __init__(self, csv_file_path, yaml_dir_path, yaml_mapping_file, transformation_per_strategy_dict):
        """
        Initializes the TransformationUtils class with the given parameters.

        Args:
            csv_file_path (str): The file path to the CSV file containing strategy definitions.
            yaml_dir_path (str): The directory path where YAML files are located.
            yaml_mapping_file (str): The file name of the YAML mapping file.
            transformation_per_strategy_dict (dict): A dictionary containing transformations per strategy.

        Attributes:
            csv_file_path (str): The file path to the CSV file containing strategy definitions.
            strategy_definitions_df (pd.DataFrame): DataFrame containing strategy definitions loaded from the CSV file.
            yaml_dir_path (str): The directory path where YAML files are located.
            yaml_mapping_file (str): The file name of the YAML mapping file.
            mapping (dict): The loaded YAML mapping.
            transformations_per_strategy_dict (dict): A dictionary containing transformations per strategy.
        """
        self.csv_file_path = csv_file_path
        self.strategy_definitions_df = self.load_strategy_definitions_csv()
        self.yaml_dir_path = yaml_dir_path
        self.yaml_mapping_file = yaml_mapping_file
        self.mapping = self.load_yaml_mapping()
        self.transformations_per_strategy_dict = transformation_per_strategy_dict
    
    def load_strategy_definitions_csv(self):
        """
        Loads a CSV file into a pandas DataFrame. If the file is not found, it creates an empty DataFrame with predefined columns.
        
        Returns:
            pd.DataFrame: DataFrame containing the CSV data or an empty DataFrame if the file is not found.
        
        Raises:
            FileNotFoundError: If the CSV file is not found.
            Exception: For any other exceptions that occur during the loading of the CSV file.
        """
        try:
            df = pd.read_csv(self.csv_file_path)
            # Convert 'strategy_id' to integers, handle any non-integer values
            df['strategy_id'] = pd.to_numeric(df['strategy_id'], errors='coerce')
            df['strategy_id'] = df['strategy_id'].fillna(0).astype(int)
            return df
        except FileNotFoundError:
            print(f"{self.csv_file_path} not found. Creating a new DataFrame.")
            columns = ['strategy_id', 'strategy_code', 'strategy', 'description', 'transformation_specification']
            return pd.DataFrame(columns=columns)
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None

        
    def load_yaml_mapping(self):
        """
        Load the YAML mapping file and return the 'strategy_groups' section.

        This method attempts to open and read a YAML file specified by 
        `self.yaml_mapping_file`. If successful, it returns the 'strategy_groups' 
        section of the YAML file as a dictionary. If the file is not found or 
        another error occurs during the loading process, it prints an error 
        message and returns an empty dictionary.

        Returns:
            dict: The 'strategy_groups' section of the YAML file if successful, 
                  otherwise an empty dictionary.
        """
        try:
            with open(self.yaml_mapping_file, 'r') as file:
                mapping = yaml.safe_load(file)
            return mapping['strategy_groups']
        except FileNotFoundError:
            print(f"{self.yaml_mapping_file} not found.")
            return {}
        except Exception as e:
            print(f"Error loading YAML file: {e}")
            return {}
    
    def get_strategy_id(self, strategy_group):
        """
        Retrieve the next available strategy ID for a given strategy group.

        This method checks the existing strategy IDs for the specified strategy group
        and returns the next available ID within the defined range. If the strategy group
        is not recognized or the ID range is exceeded, a ValueError is raised.

        Parameters:
        strategy_group (str): The strategy group for which to retrieve the next ID.

        Returns:
        int: The next available strategy ID.

        Raises:
        ValueError: If the strategy group is unknown or the ID range is exceeded.
        """
        if strategy_group not in self.mapping:
            raise ValueError(f"Unknown strategy group: {strategy_group}")

        id_range = self.mapping[strategy_group]
        min_id, max_id = map(int, id_range.split('-'))
        existing_ids = self.strategy_definitions_df.loc[self.strategy_definitions_df['strategy_code'].str.startswith(strategy_group), 'strategy_id']

        # Ensure existing_ids is numeric
        existing_ids = pd.to_numeric(existing_ids, errors='coerce').dropna().astype(int)

        if existing_ids.empty:
            return min_id

        max_existing_id = existing_ids.max()
        next_id = max_existing_id + 1

        if next_id > max_id:
            raise ValueError(f"Exceeded ID range for {strategy_group}")

        return next_id
    
    def get_strategy_code(self, strategy_group, strategy_name):
        """
        Generates a strategy code by combining the strategy group and strategy name.
        Args:
            strategy_group (str): The group to which the strategy belongs.
            strategy_name (str): The name of the strategy.
        Returns:
            str: A string in the format "STRATEGY_GROUP:STRATEGY_NAME" where both parts are in uppercase.
        """
    
        return f"{strategy_group.upper()}:{strategy_name.upper()}"
    
    def get_transformation_specification(self, yaml_file_suffix):
        """
        Retrieves the transformation specification for a given strategy based on the provided YAML file suffix.
        This method searches for YAML files in the specified directory that match the given suffix,
        extracts transformation codes from these files, and filters them based on the strategy's
        transformation dictionary. The resulting transformation codes are concatenated into a single
        string separated by pipe symbols.
        Args:
            yaml_file_suffix (str): The suffix of the YAML files to search for.
        Returns:
            str: A string containing the filtered transformation codes separated by pipe symbols.
        """
       
        all_entries = os.listdir(self.yaml_dir_path)
        strategy_transformation_yamls = [file for file in all_entries if file.endswith(f'{yaml_file_suffix}.yaml')]
        transformation_codes = []
        
        for yaml_file in strategy_transformation_yamls:
            yaml_path = os.path.join(self.yaml_dir_path, yaml_file)
            # Open the yaml file
            with open(yaml_path, 'r') as file:
                yaml_content = yaml.safe_load(file)

            transformation_code = yaml_content['identifiers']['transformation_code']
            transformation_codes.append(transformation_code)
        
        # Filter the transformation_codes to only include the ones that are used in the strategy
        transformation_codes_filtered = [
            code for code in transformation_codes 
            if code in self.transformations_per_strategy_dict.get(f'strategy_{yaml_file_suffix}', [])
        ]
        # Join transformation codes with a pipe symbol, excluding the trailing one
        transformation_specification = '|'.join(transformation_codes_filtered)
        return transformation_specification
    
    
    def save_csv(self):
        """
        Save the DataFrame back to the CSV file.
        This method attempts to save the DataFrame stored in the `strategy_definitions_df` attribute
        to the CSV file specified by the `csv_file_path` attribute. If an error occurs during the saving
        process, an error message is printed.
        Returns:
            None
        """

        # Save the DataFrame back to the CSV file
        try:
            self.strategy_definitions_df.to_csv(self.csv_file_path, index=False)
        except Exception as e:
            print(f"Error saving CSV file: {e}")
    
    
    
    def add_strategy(self, strategy_group, description, yaml_file_suffix):
        """
        Adds or updates a strategy in the strategy definitions DataFrame.
        This method reloads the strategy definitions DataFrame to ensure it has the latest version,
        generates a strategy code, and either updates an existing strategy or adds a new one based
        on whether the strategy code already exists.
        Parameters:
        strategy_group (str): The group to which the strategy belongs.
        description (str): A description of the strategy.
        yaml_file_suffix (str): The suffix of the YAML file associated with the strategy.
        Raises:
        ValueError: If the generated strategy code already exists when trying to add a new strategy.
        Returns:
        None
        """
       
        # Reload the strategy_definitions_df to ensure we have the latest version
        self.strategy_definitions_df = self.load_strategy_definitions_csv()

        # Create strategy_code
        strategy_code = self.get_strategy_code(strategy_group, yaml_file_suffix)

        # Check if the strategy code already exists in strategy_definitions_df so we can update it
        if strategy_code in self.strategy_definitions_df['strategy_code'].values:
            print(f"INFO: Strategy code {strategy_code} already exists in the strategy definitions. Strategy will be updated...")

            # Get the index of the row to update
            idx = self.strategy_definitions_df.index[self.strategy_definitions_df['strategy_code'] == strategy_code].tolist()[0]

            # Update the transformation_specification
            self.strategy_definitions_df.at[idx, 'transformation_specification'] = self.get_transformation_specification(yaml_file_suffix)

            # Save the updated DataFrame to the CSV file
            self.save_csv()
            print(f"Updated row with strategy_code {strategy_code}")
        
        else: # Add a new strategy if the strategy code does not exist
            # Get the next available strategy ID
            strategy_id = self.get_strategy_id(strategy_group)

            # Generate the strategy_code and check for uniqueness
            strategy_code = self.get_strategy_code(strategy_group, yaml_file_suffix)
            if strategy_code in self.strategy_definitions_df['strategy_code'].values:
                raise ValueError(f"Strategy_code {strategy_code} already exists. Please use a different code or eliminate the existing one.")

            new_row = {
                'strategy_id': strategy_id,  # Keep as an integer
                'strategy_code': strategy_code,
                'strategy': yaml_file_suffix,
                'description': description,
                'transformation_specification': self.get_transformation_specification(yaml_file_suffix)
            }

            self.strategy_definitions_df = pd.concat([self.strategy_definitions_df, pd.DataFrame([new_row])], ignore_index=True)
            self.save_csv()
            print(f"Updated file with new row: {new_row}")

        return None

    
