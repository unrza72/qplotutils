#Directory with ui and resource files
RESOURCE_DIR = .
 
#Directory for compiled resources
COMPILED_DIR = .
 
#UI files to compile
UI_FILES = dock_properties.ui playback.ui cam_control.ui
#Qt resource files to compile
RESOURCES = resources.qrc
 
#pyuic4 and pyrcc4 binaries
<<<<<<< HEAD
PYUIC = pyuic5 --import-from=.
PYRCC = pyrcc5
PATCH = python3 patch_ui.py

=======
PYUIC = pyuic5
PYRCC = pyrcc5
 
>>>>>>> default
#################################
# DO NOT EDIT FOLLOWING
 
COMPILED_UI = $(UI_FILES:%.ui=$(COMPILED_DIR)/%.py)
COMPILED_RESOURCES = $(RESOURCES:%.qrc=$(COMPILED_DIR)/%_rc.py)
 
all : resources ui 
 
resources : $(COMPILED_RESOURCES) 
 
ui : $(COMPILED_UI)

<<<<<<< HEAD
=======


>>>>>>> default
$(COMPILED_DIR)/%.py : $(RESOURCE_DIR)/%.ui
	$(PYUIC) $< -o $@
	$(PATCH) $@

$(COMPILED_DIR)/%_rc.py : $(RESOURCE_DIR)/%.qrc
	$(PYRCC) $< -o $@
	$(PATCH) $@


clean : 
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc) 
