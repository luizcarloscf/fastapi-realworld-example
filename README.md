# ![RealWorld Example App](etc/images/logo.png)

> ### FastAPI codebase containing real world examples (CRUD, auth, advanced patterns, monitoring, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged fullstack application built with **FastAPI/SQLAlqhemy/OpenTelemetry** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **FastAPI** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.

## How it works

> Describe the general architecture of your app here

## Getting started

To install this project and all its dependencies, we use the [Poetry] software (a python packaging and dependency manager). [Poetry] helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere. You can installed with several methods, for more information checkout the documentation page about [Poetry installation].

```bash
poetry install
```

After that, it is necessary to activate the virtual environment created by [Poetry] by executing:
```bash
poetry shell
```

Then, just serve the application using an ASGI web server, in this case we are using [Uvicorn]:
```bash
uvicorn main:app 
```

## Resources

* [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
* [OpenTelemetry Python Github](https://github.com/open-telemetry/opentelemetry-python)
* [OpenTelemetry Python Contrib Github](https://github.com/open-telemetry/opentelemetry-python-contrib)
* [OpenTelemetry Demo Project](https://opentelemetry.io/docs/demo/)
* [OpenTelemetry Demo Project Github](https://github.com/open-telemetry/opentelemetry-demo)

<!-- Links -->

[Poetry]: https://python-poetry.org/
[Poetry installation]: https://python-poetry.org/docs/#installation
[Uvicorn]: https://www.uvicorn.org/