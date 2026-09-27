Here are the steps on how to make a new release.

1. Choose the version number: bump the minor version (``X.Y+1.0``) if the release adds features
   or drops support for a Python version, or the patch version (``X.Y.Z+1``) if it only contains fixes.

2. Create a ``release-VERSION`` branch from ``upstream/main``.

3. Update ``CHANGELOG.rst``: rename the ``Unreleased`` heading to the version (adjusting the
   underline length), and add the release date below it, for example::

    3.16.0
    ------

    *2026-09-27*

4. Push the branch to ``upstream`` (not to a fork, because the ``deploy`` workflow runs against
   this branch) and open a PR.

5. Wait for all checks in the PR to pass, including Read the Docs and pre-commit.ci::

    gh pr checks PR --repo pytest-dev/pytest-mock --watch

6. Start the ``deploy`` workflow manually or via::

    gh workflow run deploy.yml --repo pytest-dev/pytest-mock --ref release-VERSION -f version=VERSION

   The workflow:

   * Publishes the package to PyPI.
   * Pushes the ``vVERSION`` tag.
   * Creates the GitHub release with the generated release notes.
   * Merges the release PR.

   Do not create the tag or the GitHub release manually.

   If the final merge step fails (for example due to branch protection rules), the release has
   already been published: just merge the PR manually, using a merge commit (not squash).
