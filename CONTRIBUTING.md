# Contributing Guidelines

This document shows you how to get started with your contribution to this project.

[**ADDING A NEW APP**](#adding-a-new-app "ADDING A NEW APP")

[**OTHER CONTRIBUTIONS**](#other-contributions "OTHER CONTRIBUTIONS")

## Adding a new app

- Fork the repo:

  - <https://github.com/albertomosconi/foss-apps/fork>

- Check out a new branch from `main` and name it after the app you want to add:

  ```sh
  git checkout -b APP_NAME
  ```

- Add your app to the matching category file under `apps/`.

  - Browser apps go in `apps/browsers.json`, file managers go in `apps/file-managers.json`, and so on.
  - If a category does not exist yet, add a new `apps/<category-slug>.json` file with `title`, `emoji`, and an empty `apps` list before adding the app.
  - Keep each category's app list sorted alphabetically by `name`.
  - If a field is unknown, leave it out instead of adding an empty string.

- Use this app-object shape where the information is known:

  ```json
  {
    "name": "App Name",
    "description": "A 15 to 60 word summary of the app and why it is useful.",
    "source": "https://github.com/example/app",
    "package": "org.example.app",
    "license": "GPL-3.0-only",
    "source_host": "GitHub",
    "fdroid_package": "org.example.app",
    "izzyondroid_package": "org.example.app",
    "fdroid": "https://f-droid.org/packages/org.example.app",
    "izzyondroid": "https://apt.izzysoft.de/fdroid/index/apk/org.example.app",
    "accrescent": "https://accrescent.app/app/org.example.app",
    "obtainium": "https://github.com/example/app/releases",
    "playstore": "https://play.google.com/store/apps/details?id=org.example.app",
    "website": "https://example.org",
    "last_reviewed": "2026-06-28",
    "maintenance_status": "active",
    "archived": false,
    "deprecated": false,
    "successor": "Name a maintained successor when the original app is archived or deprecated.",
    "anti_features": ["NonFreeNet"],
    "install_sources": "F-Droid and GitHub releases are maintained by the upstream project.",
    "maintenance_notes": "Actively maintained; latest release within the last year.",
    "privacy_security_notes": "No trackers known; document any anti-features or network caveats."
  }
  ```

- Include these details in the issue or pull request:

  - Correct category file, for example `apps/browsers.json`
  - App name and package name
  - Source repository URL
  - License and source host
  - Install sources, including F-Droid, IzzyOnDroid, Accrescent, Obtainium-compatible releases, Play Store, or website links when available
  - F-Droid and IzzyOnDroid package IDs when they differ from the Android package name
  - Anti-features when published by the install source
  - Maintenance status or archive/deprecation notes
  - Last reviewed date, archive/deprecation flags, and successor/replacement notes when relevant
  - Privacy/security caveats, including anti-features, trackers, unusual permissions, or network-service dependencies

- Run the local checks before committing:

  ```sh
  py -3 scripts/build.py
  py -3 scripts/validate.py
  ```

- Commit your changes:

  ```sh
  git commit -am "app: add APP_NAME in CATEGORY_NAME"
  ```

- Push your branch and open a pull request against `main`.

## Other Contributions

There are no specific rules for any other type of contribution, feel free to send your PR.
