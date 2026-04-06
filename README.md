# ssp_transformations_handler

Utilities for preparing SSP model transformation inputs from tabular scenario
definitions.

This package helps with two recurring tasks in SSP/SISEPUEDE-style
transformation workflows:

1. Read an Excel transformation matrix that defines which transformations
   belong to each strategy and how strongly each strategy scales the default
   transformation parameters.
2. Generate strategy-specific transformation YAML files and keep a strategy
   definitions CSV in sync with those generated YAML files.

The package also includes small DataFrame and YAML helper utilities for
validating and normalizing fractional variables.

## Package Contents

The installable Python package is located in `src/ssp_transformations_handler`.
It currently exposes two modules:

- `TransformationUtils.py`: tools for creating strategy-specific YAML files and
  updating a strategy definitions CSV.
- `GeneralUtils.py`: general helpers for reading YAML, comparing DataFrame
  schemas, adding/removing columns, and checking or normalizing fraction
  variables.

`__init__.py` is currently empty, so import classes directly from the module
files:

```python
from ssp_transformations_handler.TransformationUtils import (
    TransformationYamlProcessor,
    StrategyCSVHandler,
)
from ssp_transformations_handler.GeneralUtils import GeneralUtils
```

## Installation

Install the package from the repository root:

```bash
pip install .
```

For editable development:

```bash
pip install -e .
```

The core Python dependencies are declared in `pyproject.toml`:

- `pandas`
- `pyyaml`

If you are working in the included Conda environment, create and activate it
with:

```bash
conda env create -f environment.yml
conda activate test_transformation_package
pip install -e .
```

The Conda environment pins Python 3.11 and includes development/build tools.

## Main Workflow

The package is centered around this workflow:

1. Start with an Excel workbook that contains a transformation mapping.
2. Start with a directory of base transformation YAML files.
3. Use `TransformationYamlProcessor` to merge workbook metadata, detect strategy
   columns, and generate per-strategy YAML files.
4. Use `StrategyCSVHandler` to update the SSP strategy definitions CSV so each
   strategy points to the generated transformation YAML codes.

The processor does not run the SSP model itself. It prepares supporting files
that can be consumed by a broader SSP modeling workflow.

## Expected Excel Workbook Structure

`TransformationYamlProcessor` reads two sheets from the same Excel workbook.
By default these sheets are named:

- `main`
- `yaml`

You can override those names with `main_sheet_name` and `yaml_sheet_name` when
creating the processor.

### `main` Sheet

The `main` sheet must contain these columns:

- `transformation_code`: unique transformation code used to join against the
  YAML sheet.
- `start_period`: the period used to set `parameters.vec_implementation_ramp.tp_0_ramp`.
- One or more strategy columns whose names start with `strategy`, such as
  `strategy_a`, `strategy_high_ambition`, or `strategy_01`.

Strategy columns contain scalar values. A non-empty scalar means that the
transformation should be generated for that strategy. Empty cells are skipped.

For rows where the source YAML has `parameters.magnitude`, the generated YAML
will scale that magnitude by:

```text
new magnitude = original magnitude * strategy scalar value
```

### `yaml` Sheet

The `yaml` sheet must contain `transformation_code` and the YAML metadata used
by the processor. The current implementation expects at least these columns
after the `main` and `yaml` sheets are merged:

- `transformation_code`
- `transformation_yaml_name`
- `transformation_name`
- `subsector`

`transformation_yaml_name` should be the file name of the base YAML file inside
the YAML directory passed to the processor.

## Expected YAML Structure

Generated YAMLs are based on existing base YAML files. Each base YAML file is
expected to include at least:

```yaml
identifiers:
  transformation_code: EXAMPLE_CODE
  transformation_name: Example transformation name
description: Example description
transformer: example_transformer
parameters:
  magnitude: 0.25
```

The processor also supports YAML files where `parameters` exists but
`magnitude` is missing. In that case it still writes a strategy-specific YAML,
but it prints a message asking you to check the result manually.

When a generated YAML is saved:

- `identifiers.transformation_code` becomes
  `{transformation_code}_{STRATEGY_COLUMN_UPPERCASE}`.
- `identifiers.transformation_name` becomes
  `Scaled Default Max Parameters by {scalar_val} - {subsector}: {transformation_name}`.
- `parameters.magnitude` is multiplied by the scalar value when `magnitude`
  exists.
- `parameters.vec_implementation_ramp.tp_0_ramp` is set to `start_period`.
- The output file is written to the same YAML directory with the strategy column
  suffix added before `.yaml`.

For example, if the base file is:

```text
entc_reduce_transmission_losses.yaml
```

and the strategy column is:

```text
strategy_high
```

the generated file will be:

```text
entc_reduce_transmission_losses_strategy_high.yaml
```

## Generating Strategy-Specific YAML Files

Example:

```python
from ssp_transformations_handler.TransformationUtils import TransformationYamlProcessor

mapping_excel_path = "inputs/transformation_mapping.xlsx"
yaml_dir_path = "inputs/transformations"

processor = TransformationYamlProcessor(
    scenario_mapping_excel_path=mapping_excel_path,
    yaml_dir_path=yaml_dir_path,
    main_sheet_name="main",
    yaml_sheet_name="yaml",
)

processor.process_yaml_files()
```

After running this, check the YAML directory for generated files with strategy
suffixes. The method prints progress messages for each transformation and
strategy it processes.

You can inspect the strategy columns discovered from the workbook:

```python
strategy_columns = processor.get_strategy_names()
print(strategy_columns)
```

You can also build a dictionary of transformation codes by strategy:

```python
transformations_per_strategy = processor.get_transformations_per_strategy_dict()
print(transformations_per_strategy)
```

The dictionary keys are strategy column names, and the values are transformation
codes with the uppercased strategy name appended. For example:

```python
{
    "strategy_high": [
        "ENTC_REDUCE_LOSSES_STRATEGY_HIGH",
        "TRNS_INCREASE_ELECTRICITY_STRATEGY_HIGH",
    ]
}
```

This dictionary is useful when updating the strategy definitions CSV with
`StrategyCSVHandler`.

## Updating a Strategy Definitions CSV

`StrategyCSVHandler` updates or appends rows in a strategy definitions CSV. It
uses generated YAML files to build the `transformation_specification` field.

The CSV is expected to contain these columns:

- `strategy_id`
- `strategy_code`
- `strategy`
- `description`
- `transformation_specification`

If the CSV file does not exist, the handler creates an empty DataFrame with
those columns and writes the file when `save_csv()` is called through
`add_strategy()`.

### Strategy Group Mapping YAML

`StrategyCSVHandler` also expects a YAML mapping file with a top-level
`strategy_groups` section. Each group maps to an inclusive ID range:

```yaml
strategy_groups:
  TX: "1000-1099"
  EN: "1100-1199"
```

The strategy group is used to generate:

- the next available `strategy_id` within that group's range
- the `strategy_code` in the format `{STRATEGY_GROUP}:{STRATEGY_NAME}`

### Example

```python
from ssp_transformations_handler.TransformationUtils import (
    TransformationYamlProcessor,
    StrategyCSVHandler,
)

processor = TransformationYamlProcessor(
    scenario_mapping_excel_path="inputs/transformation_mapping.xlsx",
    yaml_dir_path="inputs/transformations",
)

processor.process_yaml_files()
transformations_per_strategy = processor.get_transformations_per_strategy_dict()

handler = StrategyCSVHandler(
    csv_file_path="inputs/strategy_definitions.csv",
    yaml_dir_path="inputs/transformations",
    yaml_mapping_file="inputs/strategy_group_ranges.yaml",
    transformation_per_strategy_dict=transformations_per_strategy,
)

handler.add_strategy(
    strategy_group="TX",
    description="High ambition transport strategy",
    yaml_file_suffix="high",
)
```

This will create or update a row whose strategy code is:

```text
TX:HIGH
```

The `transformation_specification` field is built by:

1. listing YAML files in `yaml_dir_path` that end with `{yaml_file_suffix}.yaml`
2. reading each file's `identifiers.transformation_code`
3. keeping only codes present in
   `transformations_per_strategy_dict[f"strategy_{yaml_file_suffix}"]`
4. joining the remaining codes with `|`

For example:

```text
ENTC_REDUCE_LOSSES_STRATEGY_HIGH|TRNS_INCREASE_ELECTRICITY_STRATEGY_HIGH
```

## General Utilities

`GeneralUtils` contains static helper methods that can be called without
instantiating the class.

### Read YAML

```python
from ssp_transformations_handler.GeneralUtils import GeneralUtils

data = GeneralUtils.read_yaml("inputs/example.yaml")
```

### Compare Two DataFrame Schemas

```python
GeneralUtils.compare_dfs(df_example, df_input)
```

This prints:

- columns present in `df_example` but missing from `df_input`
- columns present in `df_input` but missing from `df_example`

### Add Missing Columns

```python
df_aligned = GeneralUtils.add_missing_cols(df_example, df_input)
```

This adds any columns that exist in `df_example` but not in `df_input`. Values
for added columns are copied from `df_example`.

### Remove Additional Columns

```python
df_aligned = GeneralUtils.remove_additional_cols(df_example, df_input)
```

This drops columns from `df_input` when those columns do not exist in
`df_example`.

### Normalize Energy Fraction Variables

```python
df_normalized = GeneralUtils.normalize_energy_frac_vars(
    df_to_norm=ssp_input_df,
    frac_vars_mapping_file_path="inputs/fraction_variable_mapping.xlsx",
)
```

The fraction variable mapping file is expected to be an Excel file with a
`prefix` column. For each prefix, the method finds columns in `df_to_norm` whose
names contain that prefix, computes the row-wise sum across those columns, and
divides each column by that row-wise sum. Rows with zero sums are filled with
zero after normalization.

### Check Fraction Groups

```python
GeneralUtils.check_frac_groups(
    ssp_input_df=ssp_input_df,
    frac_vars_mapping_file_path="inputs/fraction_variable_mapping.xlsx",
)
```

This reads the same mapping structure used by `normalize_energy_frac_vars()` and
prints a warning if any group's row-wise sum is outside the range `[0, 1]`.

### Check Individual Fraction Variables

```python
GeneralUtils.check_individual_frac_vars(ssp_input_df)
```

This scans columns whose names start with `frac_` and prints a warning when a
column contains values outside `[0, 1]`.

## Practical End-to-End Example

```python
from pathlib import Path

from ssp_transformations_handler.TransformationUtils import (
    TransformationYamlProcessor,
    StrategyCSVHandler,
)

project_dir = Path("inputs")
mapping_excel = project_dir / "transformation_mapping.xlsx"
yaml_dir = project_dir / "transformations"
strategy_csv = project_dir / "strategy_definitions.csv"
strategy_groups_yaml = project_dir / "strategy_group_ranges.yaml"

processor = TransformationYamlProcessor(
    scenario_mapping_excel_path=str(mapping_excel),
    yaml_dir_path=str(yaml_dir),
)

processor.process_yaml_files()

handler = StrategyCSVHandler(
    csv_file_path=str(strategy_csv),
    yaml_dir_path=str(yaml_dir),
    yaml_mapping_file=strategy_groups_yaml,
    transformation_per_strategy_dict=processor.get_transformations_per_strategy_dict(),
)

handler.add_strategy(
    strategy_group="TX",
    description="Transport strategy generated from scaled transformation YAMLs",
    yaml_file_suffix="high",
)
```

Before using this example, make sure:

- `transformation_mapping.xlsx` has `main` and `yaml` sheets with the expected
  columns.
- `transformations/` contains the base YAML files named in
  `transformation_yaml_name`.
- `strategy_group_ranges.yaml` contains a `strategy_groups` section.
- `yaml_file_suffix` matches the part of the strategy column name after
  `strategy_`. For example, the suffix `high` corresponds to the strategy column
  `strategy_high`.

## Important Behaviors and Limitations

- Existing generated YAML files may be overwritten when the source YAML contains
  `parameters.magnitude`, because `save_yaml_file()` writes the output path
  directly.
- If the source YAML does not contain `parameters.magnitude` and the generated
  YAML already exists, the processor prints a warning and skips writing it.
- `overwrite_yaml_to_default()` exists but is not implemented.
- `check_individual_frac_vars()` is implemented, although the source currently
  still contains a TODO comment.
- Most validation is done with printed messages rather than exceptions. Review
  console output after running the workflow.
- The package currently has no command-line interface; use it from Python.
- Top-level package imports are not configured because `__init__.py` is empty.
  Import from `TransformationUtils` and `GeneralUtils` directly.

## Development Notes

The package uses a `src/` layout configured in `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

Build a source distribution and wheel from the repository root with:

```bash
python -m build
```

Upload built distributions with:

```bash
python -m twine upload dist/*
```

If you make code changes, reinstall in editable mode while developing:

```bash
pip install -e .
```
