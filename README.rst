Projector Control for Kodi
==========================
Service add-on to Kodi for controling projectors with an optional RESTful API. This is intended to be used on stand-alone media centers running Kodi.

**This project is now archived as I have no need for this plugin any more. Feel free to fork and revive it if you find it useful.**

Features
--------
* Power on, off and set input on the projector when kodi starts/exits and/or screensaver activates/deactivates
* Automatically update library when projector is shut down
* Do regular library updates as long as the projector is shut down
* Power on, off or toggle projector using a REST API
* Change input source of the projector using a REST API

Requirements
------------
* py-serial
* bottle
* A supported projector connected over serial interface
* Kodi installation (only tested on Linux)

Supported Projectors
--------------------
It should be a trivial task to add support for more projectors with serial connections. However I can't test any new implementation
without having a projector of that model. While I wouldn't mind if you send me 
projectors of different brands and models, you will probably find it cheaper to learn a little python and implement it yourself.
PR:s are always welcome.

That said; if you have a projector that you want support for, please create a github
issue at https://github.com/fredrik-eriksson/kodi_projcontrol. At minimum the following information is required to implement 
support for a projector:

* connection settings (baudrate, bytesize, parity and stopbits)
* command syntax
* response syntax (for both get and set commands)
* how to verify projector is accepting commands (if possible)
* how to detect and handle error-responses 

Below is a list of currently supported projectors

Epson
#####
* TW3200
* PowerLite 820p

InFocus
#######
* IN72/IN74/IN76

Acer
####
* X1373WH
* V7500

BenQ
####
* M535 series

Usage
-----
Copy repository to your Kodi addon directory (usually ~/.kodi/addons) and rename it to 'service.projcontrol'. 

REST API
--------
Note if you use the REST API: the api provides absolutely no security; never enable it on untrusted network.

After configuring and enabling the REST API from Kodi you can test it using curl

.. code-block:: shell

  # Check power status and input source
  $ curl http://10.37.37.13:6661/power
  {
    "power": true,
    "source": "HDMI1"
  } 
  
  # Controlling power with POST request. Valid commands are "on", "off" or "toggle"
  $ curl -i -H "Content-Type: application/json" -X POST -d '"off"' http://10.37.37.13:6661/power
  HTTP/1.0 200 OK
  Content-Type: application/json
  Content-Length: 21
  Server: Werkzeug/0.9.6 Python/2.7.9
  Date: Mon, 09 Nov 2015 18:54:03 GMT

  {
    "success": true
  }
  
  # Check valid input sources
  $ curl http://10.37.37.13:6661/source
  {
    "sources": [
      "PC",
      "HDMI1",
      "Component - YCbCr",
      "HDMI2",
      "Component - YPbPr",
      "Video",
      "S-Video",
      "Component",
      "Component - Auto",
      "RCA"
    ]
  }
  
  # Set input source
  $ curl -i -H "Content-Type: application/json" -X POST -d '"HDMI1"' http://10.37.37.13:6661/source
  HTTP/1.0 200 OK
  Content-Type: application/json
  Content-Length: 21
  Server: Werkzeug/0.9.6 Python/2.7.9
  Date: Mon, 09 Nov 2015 18:54:03 GMT

  {
    "success": true
  }
