
@if "%BLENDER_DIR%."=="." goto blender_dir_not_set

"%BLENDER_DIR%\blender.exe" -P scripts\__debug__.py "blend\audiosculpture-rig - frames+glow.blend"
@exit

:blender_dir_not_set
@echo.
@echo error: BLENDER_DIR not set.
@echo.
@pause
@exit
