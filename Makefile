# Define variables
NPROCS = $(shell grep -c 'processor' /proc/cpuinfo)
MAKEFLAGS += -j$(NPROCS)
XLS_DIR := /home/pmercatoris/finance/documents/ing/xls
BEAN_DIR := /home/pmercatoris/finance/documents/ing/beancount
BEAN_CONFIG := importers/config.py
MAIN_BEAN_FILE := /home/pmercatoris/finance/main.beancount

# List all input files in the "in" directory
XLS_FILES := $(wildcard $(XLS_DIR)/**/**/*.xls)

# Convert input files to corresponding CSV files
BEAN_FILES := $(patsubst $(XLS_DIR)/%.xls, $(BEAN_DIR)/%.beancount, $(XLS_FILES))

# Target: Transform each input file to CSV
all: $(BEAN_FILES)

# Rule to convert each input file to beancount
$(BEAN_DIR)/%.beancount: $(XLS_DIR)/%.xls
	mkdir -p $(dir $@)
	venv/bin/bean-extract $(BEAN_CONFIG) $< > $@

# fava main.beancount
web:
	fava $(MAIN_BEAN_FILE)

# PHONY target to ensure it doesn't conflict with files named 'all' or 'clean'
.PHONY: all clean

# Clean target: Remove all generated CSV files
clean:
	rm -f $(BEAN_FILES)
