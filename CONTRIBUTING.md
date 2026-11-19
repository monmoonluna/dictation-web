# Project Contribution Guidelines

This document defines the coding standards and Git workflow for
**dictation-web**, built with **React** on the frontend and **Python**
on the backend.

All contributors are expected to follow these conventions to keep the
codebase consistent, readable, maintainable, and easy to review.

## 1. General principles

-   Use English for code identifiers, comments, commit messages, branch
    names, and technical documentation.
-   Prefer clear and descriptive names over abbreviations.
-   Keep functions and components focused on one responsibility.
-   Avoid duplicated logic; extract reusable functions or components
    when appropriate.
-   Do not commit secrets, credentials, access tokens, local environment
    files, or generated artifacts.
-   Follow conventions already established in the relevant part of the
    codebase if they are more specific than this document.

## 2. Naming conventions

```
  -----------------------------------------------------------------------
  Element                 Convention              Example
  ----------------------- ----------------------- -----------------------
  JavaScript variables    `camelCase`             `audioFile`,
  and functions                                   `startRecording()`

  React components        `PascalCase`            `AudioRecorder`

  React component files   `PascalCase`            `AudioRecorder.jsx`

  React Hooks             `use` + `camelCase`     `useAudioRecorder()`

  JavaScript constants    `UPPER_SNAKE_CASE` for  `MAX_FILE_SIZE`
                          true module-level       
                          constants               

  Python variables and    `snake_case`            `audio_file`,
  functions                                       `start_recording()`

  Python classes          `PascalCase`            `AudioService`

  Python constants        `UPPER_SNAKE_CASE`      `MAX_FILE_SIZE`

  Python modules          `snake_case`            `audio_service.py`

  Folders                 `kebab-case` for        `audio-recorder/`,
                          frontend; `snake_case`  `audio_service/`
                          for Python packages     
                          where appropriate       

  Boolean values          Meaningful prefixes     `isRecording`,
                                                  `has_permission`
  -----------------------------------------------------------------------
```

Avoid unclear names such as `data`, `temp`, `obj`, or `x` except in
short, obvious local contexts.

## 3. React frontend conventions

### 3.1 Components and files

-   Use functional components and React Hooks.
-   Use PascalCase for component names and component files.
-   Keep components focused; extract reusable UI or logic when a
    component becomes difficult to understand.
-   Keep state as close as practical to the components that use it.
-   Do not call Hooks conditionally or inside loops.
-   Use stable, meaningful `key` values when rendering lists; avoid
    array indices when items can be reordered or removed.

Example:

``` jsx
function AudioRecorder({ onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);

  function handleStartRecording() {
    setIsRecording(true);
  }

  return (
    <button type="button" onClick={handleStartRecording}>
      {isRecording ? "Recording..." : "Start recording"}
    </button>
  );
}

export default AudioRecorder;
```

### 3.2 JavaScript and JSX

-   Use `const` by default; use `let` only when reassignment is
    required. Avoid `var`.
-   Prefer strict equality (`===` and `!==`).
-   Use optional chaining and nullish coalescing where they improve
    clarity.
-   Keep JSX readable; extract complex conditions and calculations into
    named variables or functions.
-   Do not put business logic, API calls, or large transformations
    directly in JSX.
-   Handle loading, empty, success, and error states explicitly.

### 3.3 React Hooks

-   Custom Hooks must start with `use`.
-   Keep side effects in the appropriate Hooks, usually `useEffect`.
-   Include all required dependencies in Hook dependency arrays.
-   Clean up subscriptions, event listeners, timers, and media resources
    when the component unmounts or an effect is re-run.
-   Avoid unnecessary effects for values that can be calculated during
    rendering.

### 3.4 Suggested frontend structure

Adapt this to the existing project structure:

``` text
src/
├── assets/
├── components/
├── features/
│   └── dictation/
├── hooks/
├── layouts/
├── pages/
├── services/
├── utils/
├── App.jsx
└── main.jsx
```

-   `components/`: reusable UI components.
-   `features/`: feature-specific components and logic.
-   `hooks/`: reusable custom Hooks.
-   `services/`: API clients and backend communication.
-   `utils/`: general-purpose helper functions.
-   `pages/`: route-level screens.

Do not create folders solely to match this example if the project is
still small.

## 4. Python backend conventions

### 4.1 Style and formatting

-   Follow **PEP 8**.
-   Use `snake_case` for variables and functions, and `PascalCase` for
    classes.
-   Use `UPPER_SNAKE_CASE` for module-level constants.
-   Use 4 spaces for indentation; do not use tabs.
-   Keep lines reasonably short and format code consistently.
-   Add type hints to public functions and important service boundaries.
-   Add docstrings to public modules, classes, and functions when their
    purpose or behavior is not self-evident.

Example:

``` python
from pathlib import Path

MAX_AUDIO_SIZE_MB = 25


def validate_audio_file(file_path: Path, file_size_mb: float) -> bool:
    """Check whether the audio file meets the configured size limit."""
    return file_path.is_file() and file_size_mb <= MAX_AUDIO_SIZE_MB
```

### 4.2 Backend design

-   Separate API routing, business logic, data access, and shared
    utilities.
-   Keep route/controller functions thin; move substantial logic into
    service functions or classes.
-   Validate request data at the API boundary.
-   Use appropriate HTTP status codes and a consistent error response
    format.
-   Do not expose stack traces, internal paths, secrets, or sensitive
    data to clients.
-   Use Python's `logging` module instead of `print()` for application
    logs.
-   Use context managers (`with`) for resources that need reliable
    cleanup.
-   Handle expected exceptions explicitly; do not silently swallow
    exceptions.
-   Avoid mutable default arguments such as `items=[]`; use `None` or an
    appropriate factory.

### 4.3 Async code

-   Use `async`/`await` when supported by the framework and when the
    operation is genuinely asynchronous.
-   Do not call blocking operations directly inside an async request
    handler if they can block the event loop.
-   Make resource cleanup and cancellation behavior explicit for
    long-running tasks.

### 4.4 Suggested backend structure

Adapt this to the framework already selected by the project:

``` text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── utils/
│   └── main.py
├── tests/
├── requirements.txt
└── .env.example
```

For a small backend, a simpler structure is acceptable. Do not introduce
layers without a practical need.

## 5. API and frontend-backend integration

-   Keep API paths, request fields, response fields, and error formats
    consistent.
-   Use JSON for standard request and response bodies unless another
    format is required (for example, audio uploads).
-   Document required fields, optional fields, validation rules, and
    possible error responses.
-   Keep the backend as the source of truth for validation and
    authorization; frontend validation is for user experience, not a
    security boundary.
-   Set request timeouts where appropriate.
-   Handle network errors, non-success HTTP responses, and unexpected
    response formats on the frontend.
-   Do not expose backend secrets or private configuration to the React
    application.

## 6. Error handling, security, and configuration

-   Never commit `.env` files containing real credentials. Commit a
    sanitized `.env.example` instead.
-   Validate and sanitize untrusted input on the backend.
-   Enforce authentication and authorization on protected backend
    endpoints.
-   Restrict upload file types and sizes; do not trust a filename or
    MIME type supplied by the client alone.
-   Avoid logging passwords, tokens, session identifiers, or sensitive
    user data.
-   Use environment variables for environment-specific configuration.
-   Provide useful error messages without revealing internal
    implementation details.

## 7. Comments and documentation

-   Write comments in English.
-   Explain why a non-obvious decision exists rather than restating what
    the code does.
-   Remove obsolete comments and commented-out code.
-   Mark follow-up work with actionable TODO comments, for example:

``` python
# TODO: Add retry handling for temporary transcription provider failures.
```

-   Update documentation when changing setup steps, environment
    variables, API contracts, or user-visible behavior.

## 8. Branch naming convention

Use this format:

``` text
<type>/<short-description>
```

All branch names must be lowercase, use hyphens between words, and avoid
spaces or special characters.

  ----------------------------------------------------------------------------------
  Prefix                  Purpose                 Example
  ----------------------- ----------------------- ----------------------------------
  `feature/`              New functionality       `feature/audio-recording`

  `fix/`                  Non-urgent bug fix      `fix/login-validation`

  `hotfix/`               Urgent production fix   `hotfix/audio-upload-failure`

  `refactor/`             Code restructuring      `refactor/transcription-service`

  `docs/`                 Documentation changes   `docs/update-api-guide`

  `test/`                 Add or update tests     `test/audio-service`

  `chore/`                Maintenance and tooling `chore/configure-eslint`

  `perf/`                 Performance             `perf/optimize-audio-processing`
                          improvements            
  ----------------------------------------------------------------------------------

## 9. Commit message convention

Follow **Conventional Commits**:

``` text
<type>(<scope>): <description>
```

The scope is optional. Use a short scope such as `auth`, `dictation`,
`api`, `audio`, or `ui`.

  ------------------------------------------------------------------------------------------------
  Type                    When to use it          Example
  ----------------------- ----------------------- ------------------------------------------------
  `feat`                  Add a feature           `feat(dictation): add audio recording`

  `fix`                   Fix a bug               `fix(api): handle invalid audio format`

  `docs`                  Documentation only      `docs: update setup instructions`

  `style`                 Formatting or style     `style(ui): format recorder component`
                          changes without logic   
                          changes                 

  `refactor`              Restructure code        `refactor(audio): extract validation logic`
                          without changing        
                          behavior                

  `test`                  Add or update tests     `test(api): add transcription endpoint tests`

  `perf`                  Improve performance     `perf(audio): reduce upload memory usage`

  `build`                 Build system or         `build: update frontend dependencies`
                          dependency changes      

  `ci`                    CI/CD configuration     `ci: add backend test workflow`
                          changes                 

  `chore`                 Maintenance tasks       `chore: configure pre-commit hooks`

  `revert`                Revert a previous       `revert: feat(dictation): add audio recording`
                          commit                  
  ------------------------------------------------------------------------------------------------

Commit message rules:

-   Write messages in English.
-   Use the imperative mood (for example, `add`, `fix`, `update`).
-   Start the description with a lowercase letter.
-   Do not end the description with a period.
-   Keep each commit focused on one logical change.
-   Avoid vague messages such as `update`, `changes`, or `fix bug`.

For a complex change, add a body:

``` text
feat(dictation): add audio recording

- Request microphone permission
- Implement start and stop recording
- Handle recording errors
```

For a breaking change, add `!` after the type/scope and explain it in a
`BREAKING CHANGE:` footer.

## 10. Git workflow

Main branches:

-   `main`: stable, production-ready code.
-   `develop`: integration branch for completed features.

Workflow for a normal task:

1.  Update local `develop`.
2.  Create a task branch from `develop`.
3.  Implement the change and commit using Conventional Commits.
4.  Push the branch to GitHub.
5.  Open a Pull Request from the task branch into `develop`.
6.  Address review feedback and ensure required checks pass.
7.  Merge the PR after approval.
8.  Delete the task branch after merging.

Example:

``` bash
git switch develop
git pull origin develop

git switch -c feature/audio-recording

# Make changes
git add .
git commit -m "feat(dictation): add audio recording"

git push -u origin feature/audio-recording
# Open a PR: feature/audio-recording -> develop
```

Release workflow:

-   Open a PR from `develop` into `main`.
-   Review and verify the release changes.
-   Merge only when the release is ready.
-   Use a version tag when the project adopts versioned releases.

Do not commit directly to `main` or `develop`. Do not force-push shared
branches.

## 11. Pull Request convention

Use a Conventional Commit-style title, for example:

``` text
feat(dictation): implement audio recording
fix(api): handle invalid audio uploads
```

Every PR description should include:

``` markdown
## Description
Briefly explain the purpose of this PR.

## Changes
- Change 1
- Change 2

## Related Issues
Closes #issue_number

## Testing
- [ ] Relevant frontend tests passed
- [ ] Relevant backend tests passed
- [ ] Manual testing completed, if applicable

## Checklist
- [ ] Code follows project conventions
- [ ] No secrets or local environment files are included
- [ ] No unnecessary debug code or logs remain
- [ ] Documentation updated, if necessary
- [ ] API contract changes are documented, if applicable
```

## 12. Pull Request review and branch protection

Recommended GitHub repository settings:

-   Require Pull Requests before merging into `main` and `develop`.
-   Require at least **1 approval** before merging.
-   Require relevant CI checks to pass when CI has been configured.
-   Require conversations to be resolved before merging.
-   Disable force pushes to protected branches.
-   Restrict branch deletion for protected branches.
-   Dismiss stale approvals when new commits are pushed, if the team
    wants changes to be reviewed again.

A reviewer should check correctness, readability, tests, error handling,
security, and whether the PR is appropriately scoped.

## 13. Definition of Done

A task is ready to merge when:

-   The implementation meets the agreed requirements.
-   Relevant frontend and backend tests pass.
-   Formatting and lint checks pass, where configured.
-   No secrets, debug statements, or unrelated changes are included.
-   API or documentation changes are updated when needed.
-   The Pull Request has the required approval.
-   All required CI checks pass.
