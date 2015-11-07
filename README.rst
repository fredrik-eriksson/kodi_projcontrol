Projector Control for Kodi
==========================
Service add-on to Kodi for controling projectors with a RESTful API. This is intended to be used on stand-alone media centers running Kodi. I use it on my raspberry pi XBian installation.

Features
--------
* Power on, off or toggle projector using a RESTful API
* Change input source of the projector using a RESTful API
* Automatically update library when projector is shut down
* Do regular library updates as long as the projector is shut down

Requirements
------------
* py-serial
* Twisted
* simplejson

Supported Projectors
--------------------
* Epson TW3200

It should be a trivial task to add support for more Epson projectors; if you have one that you want support for, please contact me at projcontrol <_at_> wb9.se. The same if you have a projector that isn't from epson but still supports power and source control over serial interface; if the protocol isn't very exotic it should be fairly simple to add support for that as well.

Usage
-----
Install and configure the add-on in Kodi. After enabling the RESTful service you can test it using curl:

.. code-block:: shell

  # Check power status and input source
  $ curl http://10.37.37.13:6661/power
  {"source": "HDMI1", "power": true}
  
  # Controlling power with POST request. Valid commands are "on", "off" or "toggle"
  $ curl -i -H "Content-Type: application/json" -X POST -d '"off"' http://10.37.37.13:6661/power
  HTTP/1.1 200 OK
  Date: Sat, 27 Jun 2015 16:45:49 GMT
  Content-Length: 4
  Content-Type: application/json
  Server: TwistedWeb/13.2.0

  true
  
  # Check valid input sources
  $ curl http://10.37.37.13:6661/source
  ["PC", "HDMI1", "Component - YCbCr", "HDMI2", "Component - YPbPr", "Video", "S-Video", "Component", "Component - Auto", "RCA"]
  
  # Set input source
  $ curl -i -H "Content-Type: application/json" -X POST -d '"HDMI1"' http://10.37.37.13:6661/source
  HTTP/1.1 200 OK
  Date: Sat, 27 Jun 2015 17:34:21 GMT
  Content-Length: 4
  Content-Type: application/json
  Server: TwistedWeb/13.2.0

  true
