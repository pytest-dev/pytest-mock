1.3
---

* Add support for Python 3.6. Thanks `@hackebrot`_ for the report (`#59`_).

* ``mock.mock_open`` is now aliased as ``mocker.mock_open`` for convenience.
  Thanks `@pokidovea`_ for the PR (`#66`_).

.. _@hackebrot: https://github.com/hackebrot
.. _@pokidovea: https://github.com/pokidovea
.. _#59: https://github.com/pytest-dev/pytest-mock/issues/59
.. _#66: https://github.com/pytest-dev/pytest-mock/pull/66

1.2
---

* Try to import ``mock`` first instead of ``unittest.mock``. This gives the user flexibility
  to install a newer ``mock`` version from PyPI instead of using the one available in the
  Python distribution.
  Thanks `@wcooley`_ for the PR (`#54`_).

* ``mock.sentinel`` is now aliased as ``mocker.sentinel`` for convenience.
  Thanks `@kjwilcox`_ for the PR (`#56`_).

.. _@wcooley: https://github.com/wcooley
.. _@kjwilcox: https://github.com/kjwilcox
.. _#54: https://github.com/pytest-dev/pytest-mock/issues/54
.. _#56: https://github.com/pytest-dev/pytest-mock/pull/56

1.1
---

* From this version onward, ``pytest-mock`` is licensed under the `MIT`_ license (`#45`_).

* Now the plugin also adds introspection information on differing call arguments when
  calling helper methods such as ``assert_called_once_with``. The extra introspection
  information is similar to pytest's and can be disabled with the ``mock_traceback_monkeypatch``
  option.
  Thanks `@asfaltboy`_ for the PR (`#36`_).

* ``mocker.stub()`` now allows passing in the name for the constructed `Mock
  <https://docs.python.org/3/library/unittest.mock.html#the-mock-class>`_
  object instead of having to set it using the internal ``_mock_name`` attribute
  directly. This is useful for debugging as the name is used in the mock's
  ``repr`` string as well as related assertion failure messages.
  Thanks `@jurko-gospodnetic`_ for the PR (`#40`_).

* Monkey patching ``mock`` module for friendlier tracebacks is automatically disabled
  with the ``--tb=native`` option. The underlying
  mechanism used to suppress traceback entries from ``mock`` module does not work with that option
  anyway plus it generates confusing messages on Python 3.5 due to exception chaining (`#44`_).
  Thanks `@blueyed`_ for the report.

* ``mock.call`` is now aliased as ``mocker.call`` for convenience.
  Thanks `@jhermann`_ for the PR (`#49`_).

.. _@jurko-gospodnetic: https://github.com/jurko-gospodnetic
.. _@asfaltboy: https://github.com/asfaltboy
.. _@jhermann: https://github.com/jhermann
.. _#45: https://github.com/pytest-dev/pytest-mock/issues/45
.. _#36: https://github.com/pytest-dev/pytest-mock/issues/36
.. _#40: https://github.com/pytest-dev/pytest-mock/issues/40
.. _#44: https://github.com/pytest-dev/pytest-mock/issues/44
.. _#49: https://github.com/pytest-dev/pytest-mock/issues/49
.. _MIT: https://github.com/pytest-dev/pytest-mock/blob/master/LICENSE


1.0
---

* Fix AttributeError with ``mocker.spy`` when spying on inherited methods
  (`#42`_). Thanks `@blueyed`_ for the PR.

.. _@blueyed: https://github.com/blueyed
.. _#42: https://github.com/pytest-dev/pytest-mock/issues/42

0.11.0
------

* `PropertyMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock>`_
  is now accessible from ``mocker``.
  Thanks `@satyrius`_ for the PR (`#32`_).

* Fix regression using one of the ``assert_*`` methods in patched
  functions which receive a parameter named ``method``.
  Thanks `@sagarchalise`_ for the report (`#31`_).

.. _@sagarchalise: https://github.com/sagarchalise
.. _@satyrius: https://github.com/satyrius
.. _#31: https://github.com/pytest-dev/pytest-mock/issues/31
.. _#32: https://github.com/pytest-dev/pytest-mock/issues/32

0.10.1
------

* Fix regression in frozen tests due to ``distutils`` import dependency.
  Thanks `@The-Compiler`_ for the report (`#29`_).

* Fix regression when using ``pytest-mock`` with ``pytest-2.7.X``.
  Thanks `@akscram`_ for the report (`#28`_).

.. _@akscram: https://github.com/Chronial
.. _#28: https://github.com/pytest-dev/pytest-mock/issues/28
.. _#29: https://github.com/pytest-dev/pytest-mock/issues/29

0.10
----

* ``pytest-mock`` now monkeypatches the ``mock`` library to improve pytest output
  for failures of mock call assertions like ``Mock.assert_called_with()``.
  Thanks to `@Chronial`_ for idea and PR (`#26`_, `#27`_)!

.. _@Chronial: https://github.com/Chronial
.. _#26: https://github.com/pytest-dev/pytest-mock/issues/26
.. _#27: https://github.com/pytest-dev/pytest-mock/issues/27

0.9.0
-----

* New ``mocker.resetall`` function, which calls ``reset_mock()`` in all mocked
  objects up to that point. Thanks to `@mathrick`_ for the PR!

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

.. _@mathrick: https://github.com/mathrick
.. _@tigarmo: https://github.com/tigarmo
.. _@rouge8: https://github.com/rouge8
.. _@fogo: https://github.com/fogo
.. _@marcwebbie: https://github.com/marcwebbie
.. _@RonnyPfannschmidt: https://github.com/RonnyPfannschmidt
.. _@The-Compiler: https://github.com/The-Compiler
.. _@kmosher: https://github.com/kmosher


