Releases
========

3.14.1 (2025-08-26)
-------------------

* `#503 <https://github.com/pytest-dev/pytest-mock/pull/503>`_: Python 3.14 is now officially supported.

3.14.0 (2024-03-21)
-------------------

* `#415 <https://github.com/pytest-dev/pytest-mock/pull/415>`_: ``MockType`` and ``AsyncMockType`` can be imported from ``pytest_mock`` for type annotation purposes.

* `#420 <https://github.com/pytest-dev/pytest-mock/issues/420>`_: Fixed a regression which would cause ``mocker.patch.object`` to not being properly cleared between tests.


3.13.0 (2024-03-21)
-------------------

* `#417 <https://github.com/pytest-dev/pytest-mock/pull/417>`_: ``spy`` now has ``spy_return_list``, which is a list containing all the values returned by the spied function.
* ``pytest-mock`` now requires ``pytest>=6.2.5``.
* `#410 <https://github.com/pytest-dev/pytest-mock/pull/410>`_: pytest-mock's ``setup.py`` file is removed.
  If you relied on this file, e.g. to install pytest using ``setup.py install``,
  please see `Why you shouldn't invoke setup.py directly <https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html#summary>`_ for alternatives.

3.12.0 (2023-10-19)
-------------------

* Added support for Python 3.12.
* Dropped support for EOL Python 3.7.
* ``mocker.resetall()`` now also resets mocks created by ``mocker.create_autospec`` (`#390`_).

.. _#390: https://github.com/pytest-dev/pytest-mock/pull/390

3.11.1 (2023-06-15)
-------------------

(This release source code is identical to ``3.11.0`` except a small internal fix to deployment/CI)

* Fixed introspection for failed ``assert_has_calls`` (`#365`_).

* Updated type annotations for ``mocker.patch`` and ``mocker.spy`` (`#364`_).

.. _#365: https://github.com/pytest-dev/pytest-mock/pull/365
.. _#364: https://github.com/pytest-dev/pytest-mock/pull/364

3.11.0 (2023-06-15)
-------------------

* Fixed introspection for failed ``assert_has_calls`` (`#365`_).

* Updated type annotations for ``mocker.patch`` and ``mocker.spy`` (`#364`_).

.. _#365: https://github.com/pytest-dev/pytest-mock/pull/365
.. _#364: https://github.com/pytest-dev/pytest-mock/pull/364


3.10.0 (2022-10-05)
-------------------

* Added new ``mocker.stop(m)`` method to stop specific ``mocker.patch`` or ``mocker.spy`` calls (`#319`_).

.. _#319: https://github.com/pytest-dev/pytest-mock/pull/319

3.9.0 (2022-09-28)
------------------

* Expose ``NonCallableMagicMock`` via the ``mocker`` fixture (`#318`_).

.. _#318: https://github.com/pytest-dev/pytest-mock/pull/318

3.8.2 (2022-07-05)
------------------

- Fixed ``AsyncMock`` support for Python 3.7+ in ``mocker.async_stub`` (`#302`_).

.. _#302: https://github.com/pytest-dev/pytest-mock/pull/302

3.8.1 (2022-06-24)
------------------

* Fixed regression caused by an explicit ``mock`` dependency in the code (`#298`_).

.. _#298: https://github.com/pytest-dev/pytest-mock/issues/298

3.8.0 (2022-06-24)
------------------

* Add ``MockerFixture.async_mock`` method. Thanks `@PerchunPak`_ for the PR (`#296`_).

.. _@PerchunPak: https://github.com/PerchunPak
.. _#296: https://github.com/pytest-dev/pytest-mock/pull/296

3.7.0 (2022-01-28)
------------------

* Python 3.10 now officially supported.
* Dropped support for Python 3.6.

3.6.1 (2021-05-06)
------------------

* Fix ``mocker.resetall()`` when using ``mocker.spy()`` (`#237`_). Thanks `@blaxter`_ for the report and `@shadycuz`_ for the PR.

.. _@blaxter: https://github.com/blaxter
.. _@shadycuz: https://github.com/shadycuz
.. _#237: https://github.com/pytest-dev/pytest-mock/issues/237

3.6.0 (2021-04-24)
------------------

* pytest-mock no longer supports Python 3.5.

* Correct type annotations for ``mocker.patch.object`` to also include the string form.
  Thanks `@plannigan`_ for the PR (`#235`_).

* ``reset_all`` now supports ``return_value`` and ``side_effect`` keyword arguments. Thanks `@alex-marty`_ for the PR (`#214`_).

.. _@alex-marty: https://github.com/alex-marty
.. _@plannigan: https://github.com/plannigan
.. _#214: https://github.com/pytest-dev/pytest-mock/pull/214
.. _#235: https://github.com/pytest-dev/pytest-mock/pull/235

3.5.1 (2021-01-10)
------------------

* Use ``inspect.getattr_static`` instead of resorting to ``object.__getattribute__``
  magic. This should better comply with objects which implement a custom descriptor
  protocol. Thanks `@yesthesoup`_ for the PR (`#224`_).

.. _@yesthesoup: https://github.com/yesthesoup
.. _#224: https://github.com/pytest-dev/pytest-mock/pull/224

3.5.0 (2021-01-04)
------------------

* Now all patch functions will emit a warning instead of raising a ``ValueError`` when used
  as a context-manager. Thanks `@iforapsy`_ for the PR (`#221`_).

* Additionally, ``mocker.patch.context_manager`` is available when the user intends to mock
  a context manager (for example  ``threading.Lock`` object), which will not emit that
  warning.

.. _@iforapsy: https://github.com/iforapsy
.. _#221: https://github.com/pytest-dev/pytest-mock/pull/221

3.4.0 (2020-12-15)
------------------

* Add `mock.seal` alias to the `mocker` fixture (`#211`_). Thanks `@coiax`_ for the PR.

* Fixed spying on exceptions not covered by the ``Exception``
  superclass (`#215`_), like ``KeyboardInterrupt`` -- PR `#216`_
  by `@webknjaz`_.

  Before the fix, both ``spy_return`` and ``spy_exception``
  were always assigned to ``None``
  whenever such an exception happened. And after this fix,
  ``spy_exception`` is set to a correct value of an exception
  that has actually happened.

.. _@coiax: https://github.com/coiax
.. _@webknjaz: https://github.com/sponsors/webknjaz
.. _#211: https://github.com/pytest-dev/pytest-mock/pull/211
.. _#215: https://github.com/pytest-dev/pytest-mock/issues/215
.. _#216: https://github.com/pytest-dev/pytest-mock/pull/216

3.3.1 (2020-08-24)
------------------

* Introduce ``MockFixture`` as an alias to ``MockerFixture``.

  Before ``3.3.0``, the fixture class was named ``MockFixture``, but was renamed to ``MockerFixture`` to better
  match the ``mocker`` fixture. While not officially part of the API, it was later discovered that this broke
  the code of some users which already imported ``pytest_mock.MockFixture`` for type annotations, so we
  decided to reintroduce the name as an alias.

  Note however that this is just a stop gap measure, and new code should use ``MockerFixture`` for type annotations.

* Improved typing for ``MockerFixture.patch``  (`#201`_). Thanks `@srittau`_ for the PR.

.. _@srittau: https://github.com/srittau
.. _#201: https://github.com/pytest-dev/pytest-mock/pull/201


3.3.0 (2020-08-21)
------------------

* ``pytest-mock`` now includes inline type annotations and exposes them to user programs. The ``mocker`` fixture returns ``pytest_mock.MockerFixture``, which can be used to annotate your tests:

  .. code-block:: python

        from pytest_mock import MockerFixture

        def test_foo(mocker: MockerFixture) -> None:
            ...

  The type annotations were developed against mypy version ``0.782``, the
  minimum version supported at the moment. If you run into an error that you believe to be incorrect, please open an issue.

  Many thanks to `@staticdev`_ for providing the initial patch (`#199`_).

.. _@staticdev: https://github.com/staticdev
.. _#199: https://github.com/pytest-dev/pytest-mock/pull/199

3.2.0 (2020-07-11)
------------------

* `AsyncMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock>`__ is now exposed in ``mocker`` and supports provides assertion introspection similar to ``Mock`` objects.

  Added by `@tirkarthi`_ in `#197`_.

.. _@tirkarthi: https://github.com/tirkarthi
.. _#197: https://github.com/pytest-dev/pytest-mock/pull/197

3.1.1 (2020-05-31)
------------------

* Fixed performance regression caused by the ``ValueError`` raised
  when ``mocker`` is used as context manager (`#191`_).

.. _#191: https://github.com/pytest-dev/pytest-mock/issues/191

3.1.0 (2020-04-18)
------------------

* New mocker fixtures added that allow using mocking functionality in other scopes:

  * ``class_mocker``
  * ``module_mocker``
  * ``package_mocker``
  * ``session_mocker``

  Added by `@scorphus`_ in `#182`_.

.. _@scorphus: https://github.com/scorphus
.. _#182: https://github.com/pytest-dev/pytest-mock/pull/182

3.0.0 (2020-03-31)
------------------

* Python 2.7 and 3.4 are no longer supported. Users using ``pip 9`` or later will install
  a compatible version automatically.

* ``mocker.spy`` now also works with ``async def`` functions (`#179`_). Thanks `@frankie567`_ for the PR!

.. _#179: https://github.com/pytest-dev/pytest-mock/issues/179
.. _@frankie567: https://github.com/frankie567

2.0.0 (2020-01-04)
------------------

Breaking Changes
++++++++++++++++

* ``mocker.spy`` attributes for tracking returned values and raised exceptions of its spied functions
  are now called ``spy_return`` and ``spy_exception``, instead of reusing the existing
  ``MagicMock`` attributes ``return_value`` and ``side_effect``.

  Version ``1.13`` introduced a serious regression: after a spied function using ``mocker.spy``
  raises an exception, further calls to the spy will not call the spied function,
  always raising the first exception instead: assigning to ``side_effect`` causes
  ``unittest.mock`` to behave this way (`#175`_).

* The deprecated ``mock`` alias to the ``mocker`` fixture has finally been removed.

.. _#175: https://github.com/pytest-dev/pytest-mock/issues/175


1.13.0 (2019-12-05)
-------------------

* The object returned by ``mocker.spy`` now also tracks any side effect
  of the spied method/function.

1.12.1 (2019-11-20)
-------------------

* Fix error if ``mocker.patch`` is used in code where the source file
  is not available, for example stale ``.pyc`` files (`#169`_).

.. _#169: https://github.com/pytest-dev/pytest-mock/issues/169#issuecomment-555729265

1.12.0 (2019-11-19)
-------------------

* Now all patch functions also raise a ``ValueError`` when used
  as a context-manager. Thanks `@AlexGascon`_ for the PR (`#168`_).

.. _@AlexGascon: https://github.com/AlexGascon
.. _#168: https://github.com/pytest-dev/pytest-mock/pull/168

1.11.2 (2019-10-19)
-------------------

* The *pytest introspection follows* message is no longer shown
  if there is no pytest introspection (`#154`_).
  Thanks `@The-Compiler`_ for the report.

* ``mocker`` now raises a ``ValueError`` when used as a context-manager.
  Thanks `@binarymason`_ for the PR (`#165`_).

.. _#154: https://github.com/pytest-dev/pytest-mock/issues/154
.. _#165: https://github.com/pytest-dev/pytest-mock/pull/165
.. _@binarymason: https://github.com/binarymason

1.11.1 (2019-10-04)
-------------------

* Fix ``mocker.spy`` on Python 2 when used on non-function objects
  which implement ``__call__`` (`#157`_). Thanks `@pbasista`_  for
  the report.

.. _#157: https://github.com/pytest-dev/pytest-mock/issues/157
.. _@pbasista: https://github.com/pbasista

1.11.0
------

* The object returned by ``mocker.spy`` now also tracks the return value
  of the spied method/function.

1.10.4
------

* Fix plugin when 'terminal' plugin is disabled

1.10.3
------

* Fix test suite in Python 3.8. Thanks `@hroncok`_ for the report and `@blueyed`_ for the PR (`#140`_).

.. _#140: https://github.com/pytest-dev/pytest-mock/pull/140
.. _@hroncok: https://github.com/hroncok

1.10.2
------

* Fix bug at the end of the test session when a call to ``patch.stopall`` is done explicitly by
  user code. Thanks `@craiga`_ for the report (`#137`_).

.. _#137: https://github.com/pytest-dev/pytest-mock/issues/137
.. _@craiga: https://github.com/craiga

1.10.1
------

* Fix broken links and update README. Also the code is now formatted using `black <https://github.com/ambv/black>`__.

1.10.0
------

* Add support for the recently added ``assert_called`` method in Python 3.6 and ``mock-2.0``. Thanks `@rouge8`_ for the PR (`#115`_).

.. _#115: https://github.com/pytest-dev/pytest-mock/pull/115

1.9.0
-----

* Add support for the recently added ``assert_called_once`` method in Python 3.6 and ``mock-2.0``. Thanks `@rouge8`_ for the PR (`#113`_).

.. _#113: https://github.com/pytest-dev/pytest-mock/pull/113


1.8.0
-----

* Add aliases for ``NonCallableMock`` and ``create_autospec`` to ``mocker``. Thanks `@mlhamel`_ for the PR (`#111`_).

.. _#111: https://github.com/pytest-dev/pytest-mock/pull/111

1.7.1
-----

* Fix ``setup.py`` to correctly read the ``README.rst``. Thanks `@ghisvail`_ for the fix (`#107`_).

.. _#107: https://github.com/pytest-dev/pytest-mock/issues/107

1.7.0
-----

**Incompatible change**

* ``pytest-mock`` no longer supports Python 2.6 and Python 3.3, following the lead of
  ``pytest`` and other projects in the community. Thanks `@hugovk`_ for the PR (`#96`_).

**Packaging**

* Fix ``mock`` requirement in Python 2. Thanks `@ghisvail`_ for the report (`#101`_).

**Internal**

* Some tests in ``pytest-mock``'s suite are skipped if assertion rewriting is disabled (`#102`_).

.. _@ghisvail: https://github.com/ghisvail
.. _@hugovk: https://github.com/hugovk
.. _#96: https://github.com/pytest-dev/pytest-mock/pull/96
.. _#101: https://github.com/pytest-dev/pytest-mock/issues/101
.. _#102: https://github.com/pytest-dev/pytest-mock/issues/102

1.6.3
-----

* Fix ``UnicodeDecodeError`` during assert introspection in ``assert_called_with`` in Python 2.
  Thanks `@AndreasHogstrom`_ for the report (`#91`_).


.. _@AndreasHogstrom: https://github.com/AndreasHogstrom

.. _#91: https://github.com/pytest-dev/pytest-mock/issues/91

1.6.2
-----

* Provide source package in ``tar.gz`` format and remove obsolete ``MANIFEST.in``.

1.6.1
-----

* Fix ``mocker.resetall()`` by ignoring mocker objects which don't have a
  ``resetall`` method, like for example ``patch.dict``.
  Thanks `@jdavisp3`_ for the PR (`#88`_).

.. _@jdavisp3: https://github.com/jdavisp3

.. _#88: https://github.com/pytest-dev/pytest-mock/pull/88

1.6.0
-----

* The original assertions raised by the various ``Mock.assert_*`` methods
  now appear in the failure message, in addition to the message obtained from
  pytest introspection.
  Thanks `@quodlibetor`_ for the initial patch (`#79`_).

.. _@quodlibetor: https://github.com/quodlibetor

.. _#79: https://github.com/pytest-dev/pytest-mock/pull/79

1.5.0
-----

* New ``mocker.mock_module`` variable points to the underlying mock module being used
  (``unittest.mock`` or ``mock``).
  Thanks `@blueyed`_ for the request (`#71`_).

.. _#71: https://github.com/pytest-dev/pytest-mock/pull/71

1.4.0
-----

* New configuration variable, ``mock_use_standalone_module`` (defaults to ``False``). This forces
  the plugin to import ``mock`` instead of ``unittest.mock`` on Python 3. This is useful to import
  a newer version than the one available in the Python distribution.

* Previously the plugin would first try to import ``mock`` and fallback to ``unittest.mock``
  in case of an ``ImportError``, but this behavior has been removed because it could hide
  hard to debug import errors (`#68`_).

* Now ``mock`` (Python 2) and ``unittest.mock`` (Python 3) are lazy-loaded to make it possible to
  implement the new ``mock_use_standlone_module`` configuration option. As a consequence of this
  the undocumented ``pytest_mock.mock_module`` variable, which pointed to the actual mock module
  being used by the plugin, has been removed.

* `DEFAULT <https://docs.python.org/3/library/unittest.mock.html#default>`_ is now available from
  the ``mocker`` fixture.

.. _#68: https://github.com/pytest-dev/pytest-mock/issues/68

1.3.0
-----

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

* ``mocker.stub()`` now allows passing in the name for the constructed ``Mock``
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

.. _@fogo: https://github.com/fogo
.. _@kmosher: https://github.com/kmosher
.. _@marcwebbie: https://github.com/marcwebbie
.. _@mathrick: https://github.com/mathrick
.. _@mlhamel: https://github.com/mlhamel
.. _@RonnyPfannschmidt: https://github.com/RonnyPfannschmidt
.. _@rouge8: https://github.com/rouge8
.. _@The-Compiler: https://github.com/The-Compiler
.. _@tigarmo: https://github.com/tigarmo
