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