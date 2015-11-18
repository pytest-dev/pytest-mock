0.8.1
-----

* ``pytest-mock`` is now also available as a wheel. Thanks `@rouge8`_ for the PR!

0.8.0
-----

* ``mock.ANY`` is now accessible from the mocker fixture (`#17`_), thanks `@tigarmo`_ for the PR!

.. _#17: https://github.com/pytest-dev/pytest-qt/issues/17

0.7.0
-----

Thanks to `@fogo`_, mocker.spy can now prey upon staticmethods and classmethods. :smile:

0.6.0
-----

* Two new auxiliary methods, ``spy`` and ``stub``. See ``README`` for usage.
(Thanks `@fogo`_ for complete PR!)


0.5.0
-----

* ``Mock`` and ``MagicMock`` are now accessible from the ``mocker`` fixture,
  many thanks to `@marcwebbie`_ for the complete PR!

0.4.3
-----

* ``mocker`` fixture now returns the same object (`#8`_). Many thanks to `@RonnyPfannschmidt`_ for the PR!

.. _#8: https://github.com/pytest-dev/pytest-qt/issues/8

0.4.2
-----

* Small fix, no longer using wheel as an alternate package since it
  conditionally depends on mock module based on Python version,
  as Python >= 3.3 already includes ``unittest.mock``.
  Many thanks to `@The-Compiler`_ for letting me know and providing a PR with the fix!

0.4.1
-----

* Small release that just uses ``pytest_mock`` as the name of the plugin,
  instead of ``pytest-mock``: this makes it simple to depend on this plugin
  explicitly using ``pytest_plugins`` module variable mechanism.

0.4.0
-----

* Changed fixture name from ``mock`` into ``mocker`` because it conflicted
  with the actual mock module, which made using it awkward when access to both
  the module and the fixture were required within a test.

  Thanks `@kmosher`_ for request and discussion in `#4`_. :smile:

.. _#4: https://github.com/pytest-dev/pytest-qt/issues/4


0.3.0
-----

* Fixed bug `#2`_, where a patch would not be uninstalled correctly after
  patching the same object twice.

0.2.0
-----

* Added ``patch.dict`` support.

0.1.0
-----

First release.

.. _#2: https://github.com/pytest-dev/pytest-qt/issues/2

.. _@tigarmo: https://github.com/tigarmo
.. _@rouge8: https://github.com/rouge8
.. _@fogo: https://github.com/fogo
.. _@marcwebbie: https://github.com/marcwebbie
.. _@RonnyPfannschmidt: https://github.com/RonnyPfannschmidt
.. _@The-Compiler: https://github.com/The-Compiler
.. _@kmosher: https://github.com/kmosher


