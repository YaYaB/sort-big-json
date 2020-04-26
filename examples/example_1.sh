INPUT_FILE="./sample_1.ljson"
NB_LINES=100000
OUTPUT_FILE="./sample_1_sorted.ljson"
BATCH_SIZE=10000

# Generate random file
echo "Generate random file ${INPUT_FILE} containing ${NB_LINES}"
#generate-random-json-file --path_file "${INPUT_FILE}" --nb_lines "${NB_LINES}" --suffix ".ljson"

# Sort the file created
echo "Sort the file ${INPUT_FILE} to ${OUTPUT_FILE}"
sort-big-json --input_file "${INPUT_FILE}" --batch_size "${BATCH_SIZE}" --output_file "$OUTPUT_FILE" --key "test.case"
echo "Done"
