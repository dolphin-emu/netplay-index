# NetPlay Index
[![Build Status](https://github.com/dolphin-emu/netplay-index/actions/workflows/run-tests.yml/badge.svg)](https://github.com/dolphin-emu/netplay-index/actions/workflows/run-tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/dolphin-emu/netplay-index/badge.svg?branch=master)](https://coveralls.io/github/dolphin-emu/netplay-index?branch=master)
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

A NetPlay Index server for Dolphin.

## Features

 - Admin panel
 - Word backlisting
 - Host banning
 - Serverlist filtering

## Requirements

- Python 3 and Poetry
- [GeoLite2 Country](https://dev.maxmind.com/geoip/geoip2/geolite2/)

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency
management.

```bash
# Install dependencies (use --no-dev to skip optional dev dependencies).
poetry install

# Run tests (Optional)
poetry run pytest

# Creates a sysop account and gives you a randomly generated password (can be changed later)
poetry run netplay-index --add_sysop=SYSOP_NAME

# Run the server
poetry run netplay-index
```

## Contributing

All PRs must be formatted using [Black](https://github.com/ambv/black) before submission and pass the CI.

Also remember to write some tests if you add any new code.  
coveralls.io will report how your PR affects the project coverage.

## License

Licensed under the GNU General Public License v3 or any later version at your option.
See [LICENSE](LICENSE).

