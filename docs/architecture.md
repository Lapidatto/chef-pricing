# Architecture

The project follows this flow:

```text
PySide6 -> ChefPricingApp -> domain services -> repositories -> CSV
```

`domain` contains models and exceptions without dependencies on the interface
or files. `application` coordinates use cases, calculations, validation, and
exports. `infrastructure` implements schemas, the workspace, atomic writes, and
repositories. `frontend` contains onboarding, navigation, tables, and PySide6
forms.

There is no HTTP server. The application is local, offline, and Windows-first.
