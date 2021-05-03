# Raven

Waterfall's media transcoder backend.

**This is a work-in-progress rewrite of Raven**, remaining API compatible with the original (which lives in the `raven/` directory of the main Waterfall repository).

Things to do on this rewrite:

* [x] CLI handling
* [x] Configuration walkthrough (`wfraven setup`)
* [x] Database pointer updater (`wfraven pointer`)
* [x] Flask application skeleton (`wfraven run`)
* [ ] Working transcoding
    * [x] Image/art posts
    * [ ] Video posts
    * [ ] Audio posts
* [ ] GPU offloading support (using `pyvidia`)
* [ ] Ease of use helpers
    * [ ] Example systemd unit
    * [ ] Example launchd plist

## Setting up

```shell
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip3 install -U .[build]
$ python3 -m wfraven setup
```

## Running

```shell
$ python3 -m wfraven run
```

## License

Copyright (C) 2018 - 2021 Benjamin Clarke, Chaos Ideal Ltd, and other contributors (see [AUTHORS.md](AUTHORS.md)). Individual components may have their own licenses.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see https://www.gnu.org/licenses/.
