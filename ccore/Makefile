PYTHON ?= python
PKG_CONFIG ?= pkg-config
TARGET = _ccore.so

SRCS = currency.c amount.c py_ccore.c
OBJS = $(SRCS:%.c=%.o)

CC = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('CC'))")
BLDSHARED = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('BLDSHARED'))")
BLDLIBRARY = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('BLDLIBRARY'))")
CFLAGS_PY = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('CFLAGS'))")
CFLAGSFORSHARED = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('CFLAGSFORSHARED'))")
INCLUDEPY = $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))")
DEFAULT_CFLAGS = -std=c99 $(CFLAGS_PY) $(CFLAGSFORSHARED) -I$(INCLUDEPY)
CFLAGS ?= $(DEFAULT_CFLAGS)
SQLITE_LIBS = $(shell $(PKG_CONFIG) --libs sqlite3)
LDFLAGS = $(SQLITE_LIBS) $(BLDLIBRARY)

.PHONY: all
all: $(TARGET)

.PHONY: check-pkg-config
check-pkg-config:
	@command -v $(PKG_CONFIG) >/dev/null 2>&1 || \
		{ echo "pkg-config is required to build the C core."; exit 1; }
	@$(PKG_CONFIG) --exists sqlite3 || \
		{ echo "pkg-config could not find sqlite3."; exit 1; }

$(TARGET): $(OBJS) | check-pkg-config
	$(BLDSHARED) $(OBJS) $(LDFLAGS) -o $@

.PHONY: clean
clean:
	-rm -rf $(OBJS) $(TARGET) $(EXECUTABLE)
