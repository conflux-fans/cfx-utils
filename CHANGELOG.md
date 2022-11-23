# CHANGELOG

## 1,0.0-beta.15

* loosen eth-* dependency versions

## 1,0.0-beta.14

* fix: python3.7 support for TypedDict and Literal

## 1.0.0-beta.13

* support python 3.7 and 3.11

## 1.0.0-beta.12

* right type hint for `combomethod`
* token unit type hints optimization
* BREAKING CHANGE: token units are now disallowed to add/sub/compare with objects rather than token units 

## 1.0.0-beta.11

* Migrate static type checking tool to Pylance because `Self` is still not supported by mypy
* type hints for `post_import_hook` and `token_unit`
* docstring for exceptions
