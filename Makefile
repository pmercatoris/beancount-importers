# Define variables
NPROCS = $(shell grep -c 'processor' /proc/cpuinfo)
MAKEFLAGS += -j$(NPROCS)
IN_DIR := import/ing/in
CSV_DIR := import/ing/csv
PY_SCRIPT := import/ing/xls2csv.py

# List all input files in the "in" directory
IN_FILES := $(wildcard $(IN_DIR)/**/*.xls)

# Convert input files to corresponding CSV files
CSV_FILES := $(patsubst $(IN_DIR)/%.xls, $(CSV_DIR)/%.csv, $(IN_FILES))

# Target: Transform each input file to CSV
all: $(CSV_FILES)

# Rule to convert each input file to CSV
$(CSV_DIR)/%.csv: $(IN_DIR)/%.xls
	mkdir -p $(dir $@)
	venv/bin/python $(PY_SCRIPT) -i $< -o $@

# PHONY target to ensure it doesn't conflict with files named 'all' or 'clean'
.PHONY: all clean

# Clean target: Remove all generated CSV files
clean:
	rm -f $(CSV_FILES)
