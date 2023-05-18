INPUT_FILE="./sample_1.ljson"
NB_LINES=10000
OUTPUT_FILE="./sample_1_sorted.ljson"
OUTPUT_FILE_REVERSE="./sample_1_sorted_reverse.ljson"
BATCH_SIZE=1000

# Generate random file
echo "Generate random file ${INPUT_FILE} containing ${NB_LINES}"
generate-random-json-file --path_file "${INPUT_FILE}" --nb_lines "${NB_LINES}" --suffix ".ljson"

# Sort the file created
echo "Sort the file ${INPUT_FILE} to ${OUTPUT_FILE}"
sort-big-json --input_file "${INPUT_FILE}" --batch_size "${BATCH_SIZE}" --output_file "$OUTPUT_FILE" --key "test.case"
echo "Done"

# Sort in reverse the file created
echo "Sort in reverse the file ${INPUT_FILE} to ${OUTPUT_FILE_REVERSE}"
sort-big-json --input_file "${INPUT_FILE}" --batch_size "${BATCH_SIZE}" --sort_order descending --output_file "$OUTPUT_FILE_REVERSE" --key "test.case"
echo "Done"
