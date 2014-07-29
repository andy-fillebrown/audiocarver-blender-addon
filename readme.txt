
- Modify blendenv.bat if your Blender install is not in the usual location.

- Run release.bat from the directory it's in to start Blender with the AudioCarver addon enabled.

- When Blender opens, go to User Preferences > Addons and turn on "Import: AudioCarver format".

- Save the User Preferences so you don't have to enable the addon every time you restart Blender.

- Under File > Import there should be a menu item for "AudioCarver (.ac)".  Run that menu item and select the AudioCarver file to import.

- Depending on the size of the AudioCarver file, importing may take a very long time, and there are no progress indicators.  I usually just keep an eye on my CPU usage to see if it's still running.  There are some messages that get displayed in the command line window, too.

- When the initial import is done I scale and move the notes with the "s" and "g" keys (holding the shift key for fine-tuning) until the highest and lowest notes are lined up in the boxes at the top of the ring.

- When the notes are in position hit the space bar and type in AudioCarver to show the AudioCarver commands, then select AudioCarver Prepare for Render.  This will reduce the complexity of the model to make it easier to render, so make sure you're all done making changes before you use that command.

- After that it's just a matter of saving the Blender file and rendering the scene using Render > Render Animation.  All the frames will go in a subdirectory called "frames" wherever you saved the .blend file.  I use VirtualDub to make them into a video and add the audio.

- When adding the audio, make sure you add 5.1 seconds of silence before it starts because that's how long it takes for the notes to get to the ring at the beginning of the video.
