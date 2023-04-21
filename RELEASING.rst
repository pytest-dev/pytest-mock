Here are the steps on how to make a new release.

1. Create a ``release-VERSION`` branch from ``upstream/master``.
2. Update ``CHANGELOG.rst``.
3. Push a branch with the changes.
4. Once all builds pass, run the ``deploy`` workflow manually.
5. Merge the PR.
