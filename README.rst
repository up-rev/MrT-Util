
MrT Framework
=============

**M**\ odular **R**\ eusability and **T**\ esting Framework

MrT is a collection of reusable modules that can be easily integrated into new projects. Each module is designed and maintained according to guidelines and standards to keep consistency. This allows uniform implementation, documentation and testing.

Modules
-------

There are three types of modules in the `MrT` framework `Platforms`, `Devices`, and `Utilities`

Platforms
~~~~~~~~~

Platforms are abstractions for specific platforms. This could be an OS or an MCU family. Each platform contains abstracted interfaces such as GPIO, Uart, SPI, and I2C. This allows the device modules to have a common interface for all platforms. When using a platform module, check the Readme for the module for the integrations steps specific to that platform. Normally these are just the steps to include the `Modules` directory in the projects include path, and define the ``MRT_PLATFORM`` symbol

Devices
~~~~~~~

Devices are modules for supporting commonly used ICs in projects. This would include common sensors, flash/eeprom memory, displays, battery charge controllers, etc.

Device modules contain all the logic needed for their operation and communicate using abstracted interfaces from platform modules

Utilities
~~~~~~~~~

Utilities are modules that provide a common functionality with no need for abstraction i.e., they do not depend on any specific hardware or platform. These include Fifos, Hashing functions, encoders/decoders, and messaging protocols. Because these do not rely on any hardware, they can be used without a ``Platform`` module

Getting Started 
===============

This section of the document gives a basic overview of installing and using the modules

Installation
------------
The code modules themselves are imported as submodules, so there are no libraries that need to be installed. But there is a toolset ``mrtutils`` which makes it easier to manage the modules. 

.. code-block:: bash

   pip install mrtutils


Integrating MrT into your project
---------------------------------


.. code-block:: bash

   cd <path/to/project>

   mrt-config <relative/path/for/MrT/root>

.. note:: If no path is provided, it will default to ./MrT and create the directory if it does not exist

This will open the ``mrt-config`` tool which allows you to select which modules you would like to integrate into your project. The UI is based on `menuconfig` to be as flexible as possible in terms of where you can run it, ie in containers or remote development environments over ssh. 

.. image:: docs/images/mrt-config.png

.. note:: MrT Modules are added as git sub-modules, if you are in a directory that does not contain a git repo, it will initialize one.

