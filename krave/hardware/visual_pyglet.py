import pyglet

display = pyglet.canvas.get_display()
screens = display.get_screens()
print("Number of screens:", len(screens))
print("width1:", screens[0].width, "height1:", screens[0].height)
print("width2:", screens[1].width, "height1:", screens[1].height)



# display = pyglet.canvas.get_display()
# screens = display.get_screens()
# window = pyglet.window.Window(screen=screens[1])
#
# @window.event
# def on_draw():
#     pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
#
# pyglet.app.run()