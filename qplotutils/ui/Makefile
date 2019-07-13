#Directory with ui and resource files
RESOURCE_DIR = .
 
#Directory for compiled resources
UI_DIR = .

PYUIC = pyuic5 --import-from=.
PYRCC = pyrcc5
PATCH = python3 patch_ui.py


UI_FILES := $(shell find $(UI_DIR) -name '*.ui')
RESOURCES := $(shell find $(RESOURCE_DIR) -name '*.qrc')

COMPILED_UI = $(UI_FILES:%.ui=%.py)
COMPILED_RESOURCES = $(RESOURCES:%.qrc=%_rc.py)
 
all : resources ui 
 
resources : $(COMPILED_RESOURCES) 
 
ui : $(COMPILED_UI)

%.py : %.ui
	$(PYUIC) $< -o $@
	$(PATCH) $@

%_rc.py : %.qrc
	$(PYRCC) $< -o $@
	$(PATCH) $@

clean : 
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc) 
