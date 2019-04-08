# NetPlay Index
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  

A NetPlay Index server for Dolphin.

## Features

 - Admin panel
 - Word backlisting
 - Host banning
 - Serverlist filtering

## Requirements

- Python 3 and pip
- [GeoLite2 Country](https://dev.maxmind.com/geoip/geoip2/geolite2/)

## Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Creates a sysop account and gives you a randomly generated password (can be changed later)
python3 main.py --add_sysop=SYSOP_NAME

# Run the server
python3 main.py
```

## Contributing

All PRs must be formatted using [Black](https://github.com/ambv/black) before submission.

## License

Licensed under the GNU General Public License v3 or any later version at your option.
See [LICENSE](LICENSE).

