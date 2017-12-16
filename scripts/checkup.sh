echo "====================== Testing CSV + COMMA ============================="
printf "\n"
slamdring \
    --input-file data/test_data_csv_comma.csv \
    --output-file data/test_data_csv_comma_answer.csv \
    --format csv \
    --delimiter ,

python scripts/equal_files.py \
    data/test_data_csv_comma_answer.csv \
    data/test_data_csv_comma_truth.csv \
    --delimiter , \
    --format csv
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "======================= Testing CSV + TAB =============================="
printf "\n"
slamdring \
    --input-file data/test_data_csv_tab.csv \
    --output-file data/test_data_csv_tab_answer.csv \
    --format csv \
    --delimiter $'\t'

python scripts/equal_files.py \
    data/test_data_csv_tab_answer.csv \
    data/test_data_csv_tab_truth.csv \
    --delimiter $'\t' \
    --format csv
printf "\n"
echo "============================== DONE ===================================="
printf "\n"


printf "\n"
echo "================== Testing CSV-HEADER + REQUEST FIELD =================="
printf "\n"
slamdring \
    --input-file data/test_data_csv_header.csv \
    --output-file data/test_data_csv_header_answer.csv \
    --format csv-header \
    --request-field request_url

python scripts/equal_files.py \
    data/test_data_csv_header_answer.csv \
    data/test_data_csv_header_truth.csv \
    --delimiter , \
    --format csv-header
printf "\n"
echo "============================== DONE ===================================="
printf "\n"


printf "\n"
echo "========================== Testing JSON ================================"
printf "\n"
slamdring \
    --input-file data/test_data_json.json \
    --output-file data/test_data_json_answer.json \
    --format json

python scripts/equal_files.py \
    data/test_data_json_answer.json \
    data/test_data_json_truth.json \
    --format json
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "=================== Testing CSV No Repeat Request ======================"
printf "\n"
slamdring \
    --input-file data/test_data_csv_comma.csv \
    --output-file data/test_data_csv_comma_no_request_answer.csv \
    --format csv \
    --no-repeat-request

python scripts/equal_files.py \
    data/test_data_csv_comma_no_request_answer.csv \
    data/test_data_csv_comma_no_request_truth.csv \
    --format csv
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "=================== Testing JSON No Repeat Request ====================="
printf "\n"
slamdring \
    --input-file data/test_data_json.json \
    --output-file data/test_data_json_no_request_answer.json \
    --format json \
    --no-repeat-request

python scripts/equal_files.py \
    data/test_data_json_no_request_answer.json \
    data/test_data_json_no_request_truth.json \
    --format json
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "===================== Testing CSV Request Field ========================"
printf "\n"
slamdring \
    --input-file data/test_data_csv_comma_request_field.csv \
    --output-file data/test_data_csv_comma_request_field_answer.csv \
    --format csv \
    --request-field 0

python scripts/equal_files.py \
    data/test_data_csv_comma_request_field_answer.csv \
    data/test_data_csv_comma_request_field_truth.csv \
    --format csv
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "=================== Testing CSV Request Field Neg ======================"
printf "\n"
slamdring \
    --input-file data/test_data_csv_comma_request_field.csv \
    --output-file data/test_data_csv_comma_request_field_answer.csv \
    --format csv \
    --request-field -2

python scripts/equal_files.py \
    data/test_data_csv_comma_request_field_answer.csv \
    data/test_data_csv_comma_request_field_truth.csv \
    --format csv
printf "\n"
echo "============================== DONE ===================================="
printf "\n"

printf "\n"
echo "================= Testing CSV-HEADER + RESPONSE FIELD =================="
printf "\n"
slamdring \
    --input-file data/test_data_csv_header.csv \
    --output-file data/test_data_csv_header_response_field_answer.csv \
    --format csv-header \
    --request-field request_url \
    --response-field response_json

python scripts/equal_files.py \
    data/test_data_csv_header_response_field_answer.csv \
    data/test_data_csv_header_response_field_truth.csv \
    --delimiter , \
    --format csv-header \
    --response-field response_json
printf "\n"
echo "============================== DONE ===================================="
printf "\n"