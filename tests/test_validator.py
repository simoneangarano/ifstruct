from ifstruct.validator import (
    check_uses_code_block,
    extract_json_from_response,
    extract_yaml_from_response,
    remove_thinking_tags,
    validate_response,
)


def test_unclosed_json_codeblock_is_not_extracted_as_raw_json():
    response = '```json\n[{"id": "1"}]'

    uses_block, block_type = check_uses_code_block(response, "json")
    data, error = extract_json_from_response(response)

    assert uses_block is False
    assert block_type is None
    assert data is None
    assert error == "Unclosed code block"


def test_unclosed_yaml_codeblock_is_not_extracted_as_raw_yaml():
    response = "```yaml\n- id: '1'"

    uses_block, block_type = check_uses_code_block(response, "yaml")
    data, error = extract_yaml_from_response(response)

    assert uses_block is False
    assert block_type is None
    assert data is None
    assert error == "Unclosed code block"


def test_validate_response_fails_unclosed_required_json_codeblock():
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
        "minItems": 1,
        "maxItems": 1,
    }
    response = '```json\n[{"id": "1"}]'

    result = validate_response(
        response=response,
        json_schema=schema,
        top_level_count=1,
        require_no_commentary=False,
        output_format="json",
        top_level_key=None,
        require_wrapper_key=False,
        require_code_block=True,
    )

    assert result.passed is False
    assert result.score == 0.0
    assert result.details["uses_code_block"] is False
    assert "Response must use a code block but none was found" in result.errors
    assert "Unclosed code block" in result.errors


def test_raw_json_and_yaml_still_parse_without_fences():
    json_data, json_error = extract_json_from_response('[{"id": "1"}]')
    yaml_data, yaml_error = extract_yaml_from_response("- id: '1'")

    assert json_error is None
    assert json_data == [{"id": "1"}]
    assert yaml_error is None
    assert yaml_data == [{"id": "1"}]


def test_string_enum_mismatch_fails_validation():
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "unit": {"type": "string", "enum": ["cup", "tsp"]},
            },
            "required": ["unit"],
        },
        "minItems": 1,
        "maxItems": 1,
    }

    result = validate_response(
        response='[{"unit": "cups"}]',
        json_schema=schema,
        top_level_count=1,
        require_no_commentary=False,
        output_format="json",
        top_level_key=None,
        require_wrapper_key=False,
        require_code_block=False,
    )

    assert result.passed is False
    assert "'cups' not in allowed values ['cup', 'tsp']" in result.errors


def test_validate_response_strips_thinking_tags():
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
        "minItems": 1,
        "maxItems": 1,
    }

    result = validate_response(
        response='<think>draft invalid junk</think>[{"id": "1"}]',
        json_schema=schema,
        top_level_count=1,
        require_no_commentary=True,
        output_format="json",
        top_level_key=None,
        require_wrapper_key=False,
        require_code_block=False,
    )

    assert result.passed is True


def test_remove_thinking_tags_handles_harmony_final_channel():
    text = "analysis notes<|start|>assistant<|channel|>final<|message|>[{\"id\":\"1\"}]<|end|>"

    assert remove_thinking_tags(text) == '[{"id":"1"}]'
