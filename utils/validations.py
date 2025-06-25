from great_expectations.data_context import FileDataContext

def validate_dataframe(df, suite_name: str, context_dir="expectations/ge_config"):
    context = FileDataContext(context_dir)
    batch = context.get_batch({
        "datasource_name": "default_pandas",
        "data_connector_name": "default_runtime_data_connector_name",
        "data_asset_name": suite_name,
        "runtime_parameters": {"batch_data": df},
        "batch_identifiers": {"default_identifier_name": "default_id"},
    })
    results = context.run_validation_operator("action_list_operator", assets_to_validate=[batch])
    return results["success"]
