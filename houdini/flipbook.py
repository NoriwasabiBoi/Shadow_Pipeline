import hou

# get scene information
cur_desktop = hou.ui.curDesktop()
scene_viewer = hou.paneTabType.SceneViewer
scene = cur_desktop.paneTabOfType(scene_viewer)
scene.flipbookSettings().stash()
flip_book_options = scene.flipbookSettings()
frame_range = hou.playbar.frameRange()

# setting flipbook settings
flip_book_options.output('%EXPORT_PATH/flipbook.$F4.jpeg') # Provide flipbook full path with padding.
flip_book_options.frameRange(frame_range) # Enter Frame Range Here in x & y
flip_book_options.useResolution(1)
flip_book_options.resolution((1080, 720)) # Based on your camera resolution

# create flipbook
scene.flipbook(scene.curViewport(), flip_book_options)
