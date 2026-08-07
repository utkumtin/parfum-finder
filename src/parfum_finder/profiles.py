"""Site profile loading, schema validation, and platform-template merging.

Fields set on a site's own profile always win over the platform template it's based
on (deep merge, site overrides platform). A profile with `platform: null` skips
template merging entirely.

TODO: write the JSON Schema files for site and platform profiles, plus the loading
and validation logic, plus tests covering the merge behavior.
"""
