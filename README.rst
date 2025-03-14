AsyncVNC2: Asynchronous VNC for Python v2
=====================================

.. image:: https://img.shields.io/badge/source-github-orange
    :target: https://github.com/andrews239/asyncvnc2

.. image:: https://readthedocs.org/projects/asyncvnc2/badge/?version=latest&style=flat-square
    :target: https://asyncvnc2.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/pypi/v/asyncvnc2?style=flat-square
    :target: https://pypi.org/project/asyncvnc2



AsyncVNC2 is a Python package which provides an asynchronous client implementation of the VNC (RFB) protocol on top of
the asyncio framework.

.. code-block::

    import asyncio, asyncvnc2

    async def run_client():
        with asyncvnc2.connect('localhost', 5900, 'username', 'password') as client:
            client.keyboard.write('hello world!')

    asyncio.run(run_client())


Features
--------

- Full support for keyboard, mouse, video and clipboard updates.

  * The frame buffer can be exported as an RGBA numpy array.
  * Keyboard keys are specified by name or character.

- Compatibility with traditional VNC servers (RealVNC, TightVNC, TigerVNC, etc).

  * Including unauthenticated connections.
  * Including password authentication with Triple DES.

- Compatibility with the built-in macOS Remote Desktop server.

  * Including username/password authentication with 2048-bit RSA keys and 128-bit AES.
  * Connects to the desktop, not the login screen.

- Detection of multi-head frame buffer data using a novel algorithm.
- Support for tunneling VNC over SSH with AsyncSSH.
- Support for image data compression with zlib.


Installation
------------

This package requires Python 3.7+.

Install AsyncVNC2 by running::

    pip install asyncvnc2


Connecting to a server
----------------------

This snippet connects to a local unauthenticated VNC server, prints information, and disconnects::

    import asyncio, asyncvnc2

    async def run_client():
        async with asyncvnc2.connect('localhost') as client:
            print(client)

    asyncio.run(run_client())

To log in to a macOS server, supply *username* and *password* arguments::

    async with asyncvnc2.connect('localhost', username='user123', password='h4x0r'):
        ...

For traditional authenticated VNC servers, the *password* argument is required but not *username*.

.. warning::

    Traditional VNC authentication is woefully insecure. For best results, configure your VNC server to listen only on
    ``127.0.0.1``. If you need external access, use an SSH tunnel.


To tunnel VNC over SSH, use the AsyncSSH package (after which this package is modelled)::

    import asyncio, asyncssh, asyncvnc2

    async def run_client():
        async with asyncssh.connect('myserver') as conn:
            async with asyncvnc2.connect('localhost', opener=conn.open_connection) as client:
                print(client)

    asyncio.run(run_client())


Sending events
--------------

Keyboard and mouse objects provide context managers for holding down keys and buttons::

    with client.keyboard.hold('Ctrl'):
        ...

    with client.mouse.hold():
        ...

The keyboard has methods for pressing keys and writing text::

    client.keyboard.press('Ctrl', 'c')  # keys are stacked
    client.keyboard.write('hi there!')  # keys are queued

The mouse has methods for moving the cursor and clicking::

    client.mouse.move(100, 200)
    client.mouse.click()
    client.mouse.right_click()
    client.mouse.scroll_up()


Taking a screenshot
-------------------

To retrieve an image from the VNC server and save it as a PNG file::

    import asyncio, asyncvnc2
    from PIL import Image

    async def run_client():
        async with asyncvnc2.connect('localhost') as client:
            # Retrieve pixels as a 3D numpy array
            pixels = await client.screenshot()

            # Save as PNG using PIL/pillow
            image = Image.fromarray(pixels)
            image.save('screenshot.png')

    asyncio.run(run_client())


The macOS VNC server composites attached monitors/screens into a single frame buffer. It does not send updates for
unoccupied regions; we can use this information to detect screens::

    pixels = client.video.as_rgba()
    for screen in client.video.detect_screens():
        screen_pixels = pixels[screen.slices]

